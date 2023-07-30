"""Provide a command-line interface."""

import logging

import click

from scrivo import __version__
from scrivo.compile import compile_site

log = logging.getLogger(__name__)


__all__ = ["present_cli"]


@click.command(
    help="Compile a static blog or website.",
    context_settings={"help_option_names": ("-h", "--help")},
)
@click.option(
    "--source",
    "-s",
    "source_dir",
    metavar="DIR",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Blog source directory.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    metavar="DIR",
    required=True,
    type=click.Path(file_okay=False),
    help="Blog destination directory.",
)
@click.option(
    "--templates",
    "-t",
    "template_dir",
    metavar="DIR",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Blog template directory.",
)
@click.option(
    "--url",
    "-u",
    "site_url",
    metavar="URL",
    type=str,
    required=True,
    help="Site root URL.",
)
@click.option(
    "--debug",
    "-d",
    "debug",
    is_flag=True,
    help="Enable debugging messages.",
)
@click.option(
    "--version",
    "-V",
    "show_version",
    is_flag=True,
    help="Show version number and exit.",
)
def present_cli(
    source_dir: str,
    output_dir: str,
    template_dir: str,
    site_url: str,
    debug: bool = False,
    show_version: bool = False,
) -> None:
    """Present a CLI for the scrivo tool.

    Args:
        source_dir: Source directory containing Markdown files
        output_dir: Destination directory
        template_dir: Templates directory
        site_url: Root URL for the site
        debug: Whether to enable debug logging
        show_version: Print the package version string and quit

    """
    if show_version:
        print(f"Scrivo CLI, package version {__version__}")
        return

    if debug:
        logging.getLogger("scrivo").setLevel("DEBUG")

    # https://stackoverflow.com/a/2991341
    ll = locals()
    for arg in ("source_dir", "output_dir", "template_dir"):
        if ll[arg] is None:
            raise ValueError(f"function argument {arg} cannot be missing")

    log.info(60 * "*")
    log.info(f"**** Beginning scrivo CLI, version {__version__}")
    log.info(60 * "*")

    log.info(f"{source_dir = }")
    log.info(f"{output_dir = }")
    log.info(f"{template_dir = }")
    log.info(f"{site_url = }")

    log.debug("Debugging messages are enabled.")
    compile_site(source_dir, output_dir, site_url, template_dir)