"""Present a command-line interface for the package."""

import logging

from scrivo.cli import present_cli

logging.basicConfig(
    level=logging.INFO,
    format="{asctime:s},{msecs:03.0f} {message}",
    style="{",
    datefmt="%-m/%-d/%y %T",
)

present_cli()
