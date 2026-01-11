"""Setup script for AI Intent Tracker."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-intent-tracker",
    version="1.0.0",
    author="Santhosh Kumar Bethi",
    author_email="santhosh.bhethi@gmail.com@gmail.com",
    description="AI-powered validation tool that ensures code changes match Jira story requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/santhoshbethi/intent_aware_git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="jira git ai validation code-review scope-creep fastapi",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "intent=cli.commands:cli",
            "git-intent=cli.commands:cli",
        ],
    },
)
