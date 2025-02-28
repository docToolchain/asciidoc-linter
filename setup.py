# setup.py - Setup configuration for the package

from setuptools import setup, find_packages

setup(
    name="asciidoc-linter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",  # Added for configuration file support
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "asciidoc-lint=asciidoc_linter.cli:main",
        ],
    },
    python_requires=">=3.8",
)