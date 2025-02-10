# setup.py - Package setup configuration
from setuptools import setup, find_packages

setup(
    name="asciidoc-linter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=5.1",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx-autodoc-typehints",
        ],
    },
    entry_points={
        "console_scripts": [
            "asciidoc-lint=asciidoc_linter.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A linter for AsciiDoc files",
    long_description=open("README.adoc").read(),
    long_description_content_type="text/x-asciidoc",
    keywords="asciidoc, linter, documentation",
    url="https://github.com/yourusername/asciidoc-linter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
