"""Command-line interface for scrivo."""

import logging

import click

from scrivo import compile
from scrivo.utils import get_package_version

log = logging.getLogger("scrivo.cli")


@click.command(context_settings={"help_option_names": ("-h", "--help")})
@click.option(
    "--source",
    "-s",
    "source_dir",
    type=click.Path(exists=True, file_okay=False),
    help="Blog source directory.",
)
@click.option(
    "--templates",
    "-t",
    "template_dir",
    type=click.Path(exists=True, file_okay=False),
    help="Blog template directory.",
)
@click.option(
    "--url",
    "-u",
    "site_url",
    type=str,
    required=True,
    help="Site root URL.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(file_okay=False),
    help="Blog destination directory.",
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
        source_dir (str): Source directory with Markdown files.
        output_dir (str): Destination directory.
        template_dir (str): Templates directory.
        site_url (str): Root URL for the site.
        debug (bool): Whether to enable debug logging.
        show_version (bool): Print the package version string and quit.

    Raises:
        ValueError: If mandatory arguments are missing. Doing
            things this way let us pass arguments like "--version"
            without failing the argument check.

    """
    if show_version:
        print(f"Scrivo CLI, package version {get_package_version()}")
        return

    if debug:
        logging.getLogger("scrivo").setLevel("DEBUG")

    # https://stackoverflow.com/a/2991341
    ll = locals()
    for arg in ("source_dir", "output_dir", "template_dir"):
        if ll[arg] is None:
            raise ValueError(f"function argument {arg} cannot be missing")

    log.info(60 * "*")
    log.info("**** Beginning scrivo CLI")
    log.info(60 * "*")

    log.info(f"{source_dir = }")
    log.info(f"{output_dir = }")
    log.info(f"{template_dir = }")
    log.info(f"{site_url = }")

    log.debug("Debugging messages are enabled.")

    compile.compile_site(source_dir, output_dir, site_url, template_dir)


if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="{message:s}", style="{")
    present_cli()
