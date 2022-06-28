"""Package setup."""

from setuptools import find_packages, setup

from scrivo.utils import get_package_version

setup(
    name="scrivo",
    version=get_package_version(),
    author="Tom Shafer",
    author_email="contact@tshafer.com",
    description="A static website generator.",
    url="https://gitlab.com/tomshafer/scrivo",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "jinja2",
        "markdown",
        "python-markdown-math",
        "bs4",
        "PyYAML",
    ],
)
