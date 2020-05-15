"""Package setup."""
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="scrivo",
    version="0.0.1",
    author="Tom Shafer",
    author_email="contact@tshafer.com",
    description="A static website generator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tomshafer/scrivo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["dateparser", "jinja2", "markdown", "python-markdown-math"],
)
