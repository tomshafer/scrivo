"""Template helpers."""
from jinja2 import Environment, FileSystemLoader


def load_from_directory(directory: str) -> Environment:
    """Produce an Environment targeted at a directory."""
    return Environment(loader=FileSystemLoader(directory))  # nosec
