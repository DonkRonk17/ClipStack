#!/usr/bin/env python3
"""
Setup script for ClipStack - Clipboard History Manager.

Install with: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="clipstack",
    version="1.0.0",
    author="ATLAS (Team Brain)",
    author_email="logan@metaphy.com",
    description="Clipboard History Manager for Power Users - Never lose a copied snippet again!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DonkRonk17/ClipStack",
    py_modules=["clipstack"],
    python_requires=">=3.8",
    install_requires=[],  # Zero dependencies!
    extras_require={
        "clipboard": ["pyperclip>=1.8.0"],  # Optional enhanced clipboard
    },
    entry_points={
        "console_scripts": [
            "clipstack=clipstack:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Desktop Environment",
    ],
    keywords="clipboard, history, manager, cli, productivity, developer-tools",
    project_urls={
        "Bug Reports": "https://github.com/DonkRonk17/ClipStack/issues",
        "Source": "https://github.com/DonkRonk17/ClipStack",
        "Documentation": "https://github.com/DonkRonk17/ClipStack#readme",
    },
)
