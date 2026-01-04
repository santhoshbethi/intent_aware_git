# AI Intent Tracker

## Overview
AI-assisted coding often makes code reviews difficult and reduces long-term quality. This repo lets developers record their intent before committing code and verifies commits against that intent.

## The Problem
With AI-powered coding assistants, developers can generate large amounts of code quickly. However, this creates challenges:
- **Difficult Code Reviews**: Reviewers struggle to understand the purpose and context of AI-generated changes
- **Reduced Long-term Quality**: Without clear intent documentation, codebases become harder to maintain
- **Lost Context**: The "why" behind code changes gets lost over time

## The Solution
AI Intent Tracker helps teams maintain code quality by:
1. Recording developer intent before making changes
2. Tracking changes against stated intentions
3. Generating automated PR summaries that include intent context
4. Providing reviewers with clear understanding of what was attempted vs. what was implemented

## Project Structure
```
ai-intent-tracker/
│
├── cli/                     # Python CLI code
│   ├── __init__.py
│   ├── commands.py          # intent start/commit/close
│   └── utils.py             # helpers
│
├── .github/
│   └── workflows/           # GitHub Actions for PR summaries
│
├── .intent/                 # Folder to store intent metadata
│
├── tests/
│   ├── test_commands.py
│   └── test_utils.py
│
├── README.md
├── requirements.txt
└── setup.py
```

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/intent_aware_git.git
cd intent_aware_git

# Install dependencies
pip install -r requirements.txt

# Install the CLI tool
pip install -e .
```

## Usage

### Starting an Intent Session
```bash
# Record your intent before starting work
intent start "Add user authentication feature with OAuth2 support"
```

### Making Your Changes
```bash
# Make your code changes as usual
# The tool tracks your git operations
```

### Committing with Intent
```bash
# Commit changes with intent verification
intent commit -m "Implement OAuth2 login flow"
```

### Closing an Intent
```bash
# Close the intent session and generate summary
intent close
```

## Features
- 🎯 **Intent Recording**: Capture what you plan to do before coding
- 🔍 **Change Verification**: Compare actual changes against stated intent
- 📊 **PR Summaries**: Automated PR descriptions with intent context
- 🔄 **GitHub Integration**: Seamless workflow integration via GitHub Actions
- 🧪 **Testing**: Comprehensive test coverage for reliability

## How It Works
1. Developer declares intent before making changes
2. Intent is stored in `.intent/` directory with metadata
3. Git operations are tracked and compared against intent
4. On commit, the tool verifies changes align with stated intent
5. GitHub Actions generate PR summaries including intent history

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
