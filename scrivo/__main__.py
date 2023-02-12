"""Present a command-line interface for the package."""

import logging

from scrivo.cli import present_cli

logging.basicConfig(level="INFO", format="{asctime:s} {message:s}", style="{")
present_cli()
