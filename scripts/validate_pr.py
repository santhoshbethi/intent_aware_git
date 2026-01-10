#!/usr/bin/env python3
"""
GitHub Actions script to validate PR commits against Jira stories.
"""

import os
import sys
import json
import subprocess
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.jira_client import JiraClient
from cli.ai_validator import AIValidator


def extract_jira_ids(base_ref, head_sha):
    """Extract Jira IDs from PR commits."""
    result = subprocess.run(
        ['git', 'log', f'origin/{base_ref}..{head_sha}', '--pretty=format:%s'],
        capture_output=True,
        text=True,
        check=True
    )
    
    commits = result.stdout
    pattern = r'\b([A-Z]{2,10}-\d+)\b'
    jira_ids = list(set(re.findall(pattern, commits)))
    
    print(f"Found Jira IDs: {jira_ids}")
    return jira_ids


def validate_commits(base_ref, head_sha):
    """Validate all commits in PR against their Jira stories."""
    jira_ids = extract_jira_ids(base_ref, head_sha)
    
    if not jira_ids:
        print("No Jira IDs found in commits")
        return {'results': [], 'critical_issues': False}
    
    jira_client = JiraClient()
    validator = AIValidator()
    results = []
    critical_issues = False
    
    # Get PR diff
    diff_result = subprocess.run(
        ['git', 'diff', f'origin/{base_ref}...{head_sha}'],
        capture_output=True,
        text=True
    )
    diff = diff_result.stdout
    
    if not diff:
        print("No code changes found")
        return {'results': [], 'critical_issues': False}
    
    for jira_id in jira_ids:
        print(f"\n=== Validating {jira_id} ===")
        
        try:
            # Fetch Jira issue
            issue = jira_client.get_issue(jira_id)
            print(f"Story: {issue['summary']}")
            
            # Validate with AI
            intent_text = jira_client.format_issue_for_validation(issue)
            validation = validator.validate_intent(intent_text, diff)
            
            score = validation.get('score', 0)
            
            result = {
                'jira_id': jira_id,
                'summary': issue['summary'],
                'score': score,
                'confidence': validation.get('confidence', 0),
                'status': validation.get('alignment', 'unknown'),
                'key_functionality_present': validation.get('key_functionality_present', False),
                'matches': validation.get('matches', []),
                'discrepancies': validation.get('discrepancies', []),
                'suggestions': validation.get('suggestions', [])
            }
            
            results.append(result)
            
            print(f"Score: {score}/10")
            
            if score < 3:
                critical_issues = True
                print(f"CRITICAL: Low alignment score!")
            
        except Exception as e:
            print(f"Error validating {jira_id}: {e}")
            results.append({
                'jira_id': jira_id,
                'error': str(e),
                'score': 0
            })
            critical_issues = True
    
    return {
        'results': results,
        'critical_issues': critical_issues
    }


def generate_pr_comment(validation_data):
    """Generate markdown comment for PR."""
    results = validation_data['results']
    
    if not results:
        return "## 🎯 Jira Story Validation Report\n\nNo Jira IDs found in commit messages."
    
    comment = "## 🎯 Jira Story Validation Report\n\n"
    
    for result in results:
        jira_id = result['jira_id']
        
        if 'error' in result:
            comment += f"### {jira_id}\n**Error:** {result['error']}\n\n"
            continue
        
        score = result['score']
        summary = result['summary']
        status = result['status']
        

        
        comment += f"###  {jira_id}: {summary}\n"
        comment += f"**Alignment Score:** {score}/10 (Confidence: {result['confidence']}%)\n"
        comment += f"**Status:** {status}\n"
        comment += f"**Key Functionality Present:** {'Yes' if result['key_functionality_present'] else 'No'}\n\n"
        
        if result.get('matches'):
            comment += "**What Aligns:**\n"
            for match in result['matches'][:3]:
                comment += f"- {match}\n"
            comment += "\n"
        
        if result.get('discrepancies'):
            comment += "**Discrepancies:**\n"
            for disc in result['discrepancies'][:3]:
                comment += f"- {disc}\n"
            comment += "\n"
        
        if result.get('suggestions'):
            comment += "**Suggestions:**\n"
            for sug in result['suggestions'][:3]:
                comment += f"- {sug}\n"
            comment += "\n"
    
    # Summary
    avg_score = sum(r['score'] for r in results if 'score' in r) / len(results)
    critical = len([r for r in results if r.get('score', 0) < 3])
    
    comment += "---\n### Summary\n"
    comment += f"- **Average Score:** {avg_score:.1f}/10\n"
    comment += f"- **Stories Validated:** {len(results)}\n"
    comment += f"- **Critical Issues:** {critical}\n"
    
    return comment


def main():
    base_ref = os.getenv('GITHUB_BASE_REF')
    head_sha = os.getenv('GITHUB_SHA')
    
    if not base_ref or not head_sha:
        print("Error: GITHUB_BASE_REF and GITHUB_SHA required")
        sys.exit(1)
    
    print(f"Validating PR: {base_ref}..{head_sha}")
    
    validation_data = validate_commits(base_ref, head_sha)
    
    # Save results
    with open('validation_results.json', 'w') as f:
        json.dump(validation_data, f, indent=2)
    
    # Generate PR comment
    comment = generate_pr_comment(validation_data)
    with open('pr_comment.md', 'w') as f:
        f.write(comment)
    
    print("\n" + "="*60)
    print("Validation Complete")
    print("="*60)
    
    if validation_data['critical_issues']:
        print("\nCRITICAL: Some stories have severe misalignment!")
        sys.exit(1)
    
    print("\n All validations passed!")
    sys.exit(0)


if __name__ == '__main__':
    main()
