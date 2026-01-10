"""Jira API client for fetching story details."""

import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self):
        """Initialize Jira client with credentials from environment."""
        self.jira_url = os.getenv('JIRA_URL')  # e.g., https://yourcompany.atlassian.net
        self.jira_email = os.getenv('JIRA_EMAIL')
        self.jira_api_token = os.getenv('JIRA_API_TOKEN')
        
        if not all([self.jira_url, self.jira_email, self.jira_api_token]):
            raise ValueError(
                "Jira credentials not found. Set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN in .env"
            )
        
        self.jira_url = self.jira_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (self.jira_email, self.jira_api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def extract_jira_id(self, commit_message):
        """
        Extract Jira issue ID from commit message.
        
        Supports formats:
        - PROJ-123: commit message
        - [PROJ-123] commit message
        - PROJ-123 commit message
        
        Args:
            commit_message: The git commit message
            
        Returns:
            str: Jira issue ID (e.g., "PROJ-123") or None
        """
        # Pattern: PROJECT-123 format (uppercase letters, dash, numbers)
        pattern = r'\b([A-Z]{2,10}-\d+)\b'
        match = re.search(pattern, commit_message)
        
        if match:
            return match.group(1)
        return None
    
    def get_issue(self, issue_key):
        """
        Fetch Jira issue details.
        
        Args:
            issue_key: Jira issue key (e.g., "PROJ-123")
            
        Returns:
            dict: Issue details including summary, description, etc.
        """
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                raise ValueError(f"Empty response from Jira API for issue {issue_key}")
            
            # Extract relevant fields
            fields = data.get('fields', {})
            
            if not fields:
                raise ValueError(f"No fields found in Jira issue {issue_key}")
            
            # Helper to safely get nested values
            def safe_get(obj, key, default=''):
                val = obj.get(key) if obj else None
                return val if val is not None else default
            
            return {
                'key': data.get('key'),
                'summary': safe_get(fields, 'summary'),
                'description': self._extract_description(fields.get('description')),
                'issue_type': safe_get(fields.get('issuetype'), 'name'),
                'status': safe_get(fields.get('status'), 'name'),
                'priority': safe_get(fields.get('priority'), 'name', 'None'),
                'assignee': safe_get(fields.get('assignee'), 'displayName', 'Unassigned'),
                'acceptance_criteria': self._extract_acceptance_criteria(fields.get('description')),
                'labels': fields.get('labels', []),
                'components': [c.get('name', '') for c in (fields.get('components') or [])],
            }
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Jira issue {issue_key} not found. Does it exist in {self.jira_url}?")
            elif e.response.status_code == 401:
                raise ValueError("Jira authentication failed. Check JIRA_EMAIL and JIRA_API_TOKEN in .env")
            elif e.response.status_code == 403:
                raise ValueError(f"Access denied to Jira issue {issue_key}. Check permissions.")
            else:
                raise ValueError(f"HTTP {e.response.status_code}: {e.response.text}")
        
        except requests.exceptions.Timeout:
            raise ValueError(f"Timeout connecting to Jira at {self.jira_url}. Check network/VPN.")
        
        except requests.exceptions.ConnectionError as e:
            raise ValueError(f"Cannot connect to Jira at {self.jira_url}. Check URL and network. Error: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Network error connecting to Jira: {str(e)}")
        
        except Exception as e:
            raise ValueError(f"Error fetching Jira issue: {str(e)}")
    
    def _extract_description(self, description_obj):
        """Extract plain text from Jira description (Atlassian Document Format)."""
        if not description_obj:
            return ""
        
        # Jira uses Atlassian Document Format (ADF)
        if isinstance(description_obj, dict):
            return self._adf_to_text(description_obj)
        
        return str(description_obj)
    
    def _adf_to_text(self, adf_obj):
        """Convert Atlassian Document Format to plain text."""
        if not isinstance(adf_obj, dict):
            return str(adf_obj)
        
        text_parts = []
        
        if adf_obj.get('type') == 'doc':
            for content in adf_obj.get('content', []):
                text_parts.append(self._adf_to_text(content))
        
        elif adf_obj.get('type') == 'paragraph':
            para_text = []
            for content in adf_obj.get('content', []):
                if content.get('type') == 'text':
                    para_text.append(content.get('text', ''))
            text_parts.append(' '.join(para_text))
        
        elif adf_obj.get('type') == 'text':
            text_parts.append(adf_obj.get('text', ''))
        
        elif adf_obj.get('type') in ['heading', 'bulletList', 'orderedList', 'listItem']:
            for content in adf_obj.get('content', []):
                text_parts.append(self._adf_to_text(content))
        
        return '\n'.join(filter(None, text_parts))
    
    def _extract_acceptance_criteria(self, description_obj):
        """Extract acceptance criteria from description if present."""
        text = self._extract_description(description_obj)
        
        # Look for common acceptance criteria patterns
        patterns = [
            r'Acceptance Criteria:?\s*\n(.+?)(?=\n\n|\Z)',
            r'AC:?\s*\n(.+?)(?=\n\n|\Z)',
            r'Criteria:?\s*\n(.+?)(?=\n\n|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def format_issue_for_validation(self, issue):
        """
        Format Jira issue into text suitable for AI validation.
        
        Args:
            issue: Issue dict from get_issue()
            
        Returns:
            str: Formatted text describing the intent
        """
        parts = [
            f"Jira Story: {issue['key']} - {issue['summary']}",
            f"Type: {issue['issue_type']}",
            f"Status: {issue['status']}",
        ]
        
        if issue['description']:
            parts.append(f"\nDescription:\n{issue['description']}")
        
        if issue['acceptance_criteria']:
            parts.append(f"\nAcceptance Criteria:\n{issue['acceptance_criteria']}")
        
        if issue['components']:
            parts.append(f"\nComponents: {', '.join(issue['components'])}")
        
        return '\n'.join(parts)
    
    def validate_commit_message_format(self, commit_message):
        """
        Validate that commit message contains Jira ID.
        
        Args:
            commit_message: The commit message to validate
            
        Returns:
            tuple: (is_valid, jira_id, error_message)
        """
        jira_id = self.extract_jira_id(commit_message)
        
        if not jira_id:
            return (False, None, 
                   "Commit message must include Jira issue ID (e.g., PROJ-123)")
        
        return (True, jira_id, None)
