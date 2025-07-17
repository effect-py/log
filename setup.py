from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="effect-log",
    version="0.1.0b1",  # Beta version
    author="effect-py",
    author_email="maintainers@effect-py.org",
    description="Functional structured logging with composable effects for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/effect-py/log",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "ruff>=0.1.0",
            "mypy>=1.0",
            "pre-commit>=2.20",
            "twine>=4.0",
        ],
    },
    keywords="logging structured functional effects composition",
    project_urls={
        "Homepage": "https://github.com/effect-py/log",
        "Documentation": "https://github.com/effect-py/log#readme",
        "Repository": "https://github.com/effect-py/log",
        "Bug Reports": "https://github.com/effect-py/log/issues",
        "Discussions": "https://github.com/orgs/effect-py/discussions",
    },
)
