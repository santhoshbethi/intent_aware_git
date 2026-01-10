"""AI-powered intent validation and vulnerability detection."""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIValidator:
    """Validate code changes against intent using AI."""
    
    def __init__(self):
        """Initialize the AI validator with OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your environment or .env file"
            )
        self.client = OpenAI(api_key=api_key)
    
    def _detect_language(self, code_diff):
        """Detect the primary programming language from diff."""
        language_patterns = {
            'Python': r'\+.*\.(py)[\s:]|import |def |class ',
            'JavaScript': r'\+.*\.(js|jsx)[\s:]|const |let |function |=>',
            'TypeScript': r'\+.*\.(ts|tsx)[\s:]|interface |type |const.*:',
            'Java': r'\+.*\.java[\s:]|public class |private |@Override',
            'Go': r'\+.*\.go[\s:]|func |package |import ',
            'Rust': r'\+.*\.rs[\s:]|fn |impl |pub ',
            'C++': r'\+.*\.(cpp|hpp)[\s:]|#include |namespace |std::',
            'Ruby': r'\+.*\.rb[\s:]|def |class |end$',
            'PHP': r'\+.*\.php[\s:]|<\?php|function |class ',
        }
        
        for lang, pattern in language_patterns.items():
            if re.search(pattern, code_diff, re.MULTILINE):
                return lang
        
        return 'Unknown'
    
    def _get_language_context(self, language):
        """Get language-specific security and best practice context."""
        contexts = {
            'Python': "Check for: SQL injection in raw queries, unsafe pickle usage, command injection via os.system, eval/exec usage.",
            'JavaScript': "Check for: XSS vulnerabilities, prototype pollution, unsafe innerHTML, eval usage, missing input sanitization.",
            'TypeScript': "Check for: Type casting bypasses, 'any' type overuse, missing null checks, unsafe type assertions.",
            'Java': "Check for: SQL injection, XML injection, deserialization vulnerabilities, path traversal.",
            'Go': "Check for: SQL injection, command injection, race conditions, error handling issues.",
            'PHP': "Check for: SQL injection, XSS, file inclusion vulnerabilities, command injection.",
            'Unknown': "Check for: Common security vulnerabilities and code quality issues."
        }
        return contexts.get(language, contexts['Unknown'])
    
    def get_intent_history(self, max_items=3):
        """Get recent intent history for context."""
        from .utils import get_intent_dir
        intent_dir = get_intent_dir()
        
        if not intent_dir.exists():
            return []
        
        history = []
        for intent_file in sorted(intent_dir.glob('intent_*.json'), reverse=True)[:max_items]:
            try:
                with open(intent_file, 'r') as f:
                    data = json.load(f)
                    # Extract validation score if exists
                    score = None
                    if data.get('commits'):
                        for commit in data['commits']:
                            if commit.get('validation', {}).get('score'):
                                score = commit['validation']['score']
                                break
                    
                    history.append({
                        'intent': data.get('message', ''),
                        'score': score,
                        'commits': len(data.get('commits', []))
                    })
            except:
                continue
        
        return history
    
    def validate_intent(self, intent_message, code_diff):
        """
        Validate if code changes align with the stated intent.
        
        Args:
            intent_message: The developer's stated intent
            code_diff: Git diff of the changes
            
        Returns:
            dict: Validation results with alignment score and explanation
        """
        # Detect language and get context
        language = self._detect_language(code_diff)
        
        # Get historical context
        history = self.get_intent_history()
        history_context = ""
        if history:
            history_context = "\n\nHistorical Context (learn from past patterns):\n"
            for h in history:
                if h['score']:
                    history_context += f"- Past intent: '{h['intent']}' achieved alignment score {h['score']}/10\n"
        
        # Build enhanced prompt with all improvements
        prompt = f"""You are an expert code reviewer analyzing intent-code alignment. BE EXTREMELY STRICT.

CRITICAL SCORING RULES:
- Score 0-2: Code does NOT implement the stated intent AT ALL (missing expected functionality)
- Score 3-4: Code barely relates to intent, mostly unrelated changes
- Score 5-6: Partial implementation, significant gaps or extra unrelated changes
- Score 7-8: Good implementation with minor gaps or slight scope issues
- Score 9-10: Perfect match, code fully implements stated intent

EXAMPLES OF SCORING:

Example 1 - ZERO ALIGNMENT (Score: 0-1):
Intent: "Add OAuth2 authentication"
Changes: Fixed typo in README, updated package version
Analysis: NO OAuth2 code added. Completely unrelated changes.
Score: 0/10 

Example 2 - ZERO ALIGNMENT (Score: 0-1):
Intent: "Implement user login with OAuth"
Changes: Added empty function stub, no actual OAuth implementation
Analysis: Intent mentions OAuth but NO OAuth libraries, flows, or authentication logic present.
Score: 1/10

Example 3 - High Alignment (Score: 9):
Intent: "Add email validation"
Changes: Added regex validator, unit tests, integrated into form
Score: 9/10 ✓

Example 4 - Scope Creep (Score: 3):
Intent: "Fix button styling"
Changes: Refactored authentication + changed database + styled button
Score: 3/10 - Way too much unrelated work

INSTRUCTIONS FOR ANALYZING GIT DIFFS:
- Lines with '+' are NEW CODE ADDED - analyze these carefully!
- Lines with '-' are CODE REMOVED
- Lines without +/- are CONTEXT (unchanged)
- BE CRITICAL: If intent says "add X" but X is NOT in the diff, score MUST be 0-2!

CURRENT ANALYSIS:
Language Detected: {language}
Developer's Stated Intent: "{intent_message}"{history_context}

Code Changes (Git Diff):
{code_diff}

STEP-BY-STEP STRICT ANALYSIS:
1. Identify the KEY FUNCTIONALITY mentioned in the intent (e.g., "OAuth", "email validation", "login")
2. Search the diff for evidence of that functionality (libraries, functions, logic)
3. If KEY FUNCTIONALITY is MISSING → Score MUST be 0-2 (NOT 5, NOT 7!)
4. If KEY FUNCTIONALITY exists but incomplete → Score 3-6
5. If KEY FUNCTIONALITY fully implemented → Score 7-10

BE BRUTALLY HONEST. Don't give high scores for good intentions - only for actual implementation.

RESPOND IN VALID JSON FORMAT ONLY:
{{
  "score": <0-10 integer>,
  "confidence": <0-100 integer>,
  "alignment": "<aligned|partially_aligned|misaligned>",
  "intent_summary": "KEY functionality developer intended to add",
  "actual_changes": "what code ACTUALLY does (be specific about what's present/missing)",
  "key_functionality_present": <true|false>,
  "matches": ["list ONLY what truly aligns"],
  "discrepancies": ["list missing functionality and out-of-scope changes"],
  "suggestions": ["how to actually implement the stated intent"],
  "risk_level": "<low|medium|high>",
  "needs_human_review": <true|false>
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except json.JSONDecodeError as e:
            return {
                'error': f'JSON parsing error: {str(e)}',
                'score': None,
                'confidence': 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'score': None,
                'confidence': 0
            }
    
    def check_vulnerabilities(self, code_diff):
        """
        Check code changes for security vulnerabilities.
        
        Args:
            code_diff: Git diff of the changes
            
        Returns:
            dict: Vulnerability analysis results
        """
        # Detect language for context-specific scanning
        language = self._detect_language(code_diff)
        lang_context = self._get_language_context(language)
        
        prompt = f"""You are a cybersecurity expert analyzing code for vulnerabilities.

Language: {language}
Language-Specific Context: {lang_context}

INSTRUCTIONS FOR ANALYZING GIT DIFFS:
- Lines with '+' are NEW CODE (analyze these carefully!)
- Lines with '-' are REMOVED CODE (less critical but note what was removed)
- Focus security analysis on the NEW code being added

Code Changes (Git Diff):
{code_diff}

COMPREHENSIVE SECURITY SCAN:

1. AUTHENTICATION & AUTHORIZATION:
   - Missing authentication checks
   - Privilege escalation risks
   - Session management issues
   - Weak password policies

2. INPUT VALIDATION:
   - SQL injection (are queries parameterized?)
   - XSS vulnerabilities (is output sanitized?)
   - Command injection risks
   - Path traversal vulnerabilities
   - LDAP/XML injection

3. DATA PROTECTION:
   - Hardcoded secrets/API keys/passwords
   - Sensitive data in logs
   - Missing encryption
   - Insecure data storage

4. CODE QUALITY & SECURITY:
   - Use of dangerous functions (eval, exec, system calls)
   - Race conditions
   - Resource exhaustion risks
   - Error handling that leaks information

5. DEPENDENCIES & CONFIGURATION:
   - Outdated or vulnerable dependencies
   - Insecure configurations
   - Missing security headers

ANALYZE SYSTEMATICALLY:
1. Identify all potential vulnerabilities
2. Assess severity for each
3. Provide specific line references if possible
4. Suggest concrete fixes

RESPOND IN VALID JSON FORMAT ONLY:
{{
  "overall_severity": "<NONE|LOW|MEDIUM|HIGH|CRITICAL>",
  "confidence": <0-100 integer>,
  "vulnerabilities": [
    {{
      "type": "sql_injection|xss|auth|secrets|etc",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "description": "detailed description",
      "location": "approximate line or context",
      "fix": "specific remediation steps"
    }}
  ],
  "safe_practices_found": ["list good security practices used"],
  "recommendations": ["prioritized security recommendations"],
  "requires_immediate_action": <true|false>
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more conservative security analysis
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except json.JSONDecodeError as e:
            return {
                'error': f'JSON parsing error: {str(e)}',
                'overall_severity': 'NONE',
                'confidence': 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'overall_severity': 'NONE',
                'confidence': 0
            }
