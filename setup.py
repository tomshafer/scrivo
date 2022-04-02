"""Package setup."""
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


def find_version() -> str:
    with open("scrivo/__init__.py") as file:
        for line in file:
            if "__version__" in line:
                return line.strip().split("=").pop().strip('" ')
    raise ValueError("Could not find version number")


setup(
    name="scrivo",
    version=find_version(),
    author="Tom Shafer",
    author_email="contact@tshafer.com",
    description="A static website generator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tomshafer/scrivo",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "jinja2",
        "markdown",
        "python-markdown-math",
        "numpy",
        "bs4",
        "scikit-learn",
        "snowballstemmer",
        "PyYAML",
    ],
    scripts=["bin/sitesync"],
)
