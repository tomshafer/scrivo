"""Package setup."""

from setuptools import find_packages, setup


def _find_version() -> str:
    class VersionNotFoundError(Exception):
        pass

    with open("scrivo/__init__.py") as file:
        for line in file:
            if "__version__" in line:
                return line.strip().split("=").pop().strip('" ')

    raise VersionNotFoundError("Could not find version number")


setup(
    name="scrivo",
    version=_find_version(),
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
        "numpy",
        "bs4",
        "scikit-learn",
        "snowballstemmer",
        "PyYAML",
        "yacs",
    ],
)
