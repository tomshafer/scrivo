"""Page rendering utilities."""

from typing import Callable

from jinja2 import Environment

from scrivo.pages import page, render_pages

# The registry tracks the various jobs needing to be done
REGISTRY: dict[str, Callable[[list[page], str, Environment], None]] = {}

# All individual pages
REGISTRY["Individual pages"] = render_pages
