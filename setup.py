"""Setup script for AI Intent Tracker."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-intent-tracker",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Track and verify coding intentions in AI-assisted development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/intent_aware_git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
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
