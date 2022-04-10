"""Command-line interface for scrivo."""

import logging

import click

from scrivo import compile

log = logging.getLogger("scrivo.cli")


@click.command(context_settings={"help_option_names": ("-h", "--help")})
@click.option(
    "--source",
    "-s",
    "source_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Blog source directory.",
)
@click.option(
    "--templates",
    "-t",
    "template_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Blog template directory.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    required=True,
    type=click.Path(file_okay=False),
    help="Blog destination directory.",
)
@click.option("--debug", "debug", is_flag=True, help="Enable debugging messages.")
def _show_cli(
    source_dir: str,
    output_dir: str,
    template_dir: str,
    debug: bool = False,
) -> None:
    if debug:
        logging.getLogger("scrivo").setLevel("DEBUG")
    log.info(60 * "*")
    log.info("**** Beginning scrivo CLI")
    log.info(60 * "*")
    log.info(f"{source_dir = }")
    log.info(f"{output_dir = }")
    log.info(f"{template_dir = }")
    log.info(f"{debug = }")
    log.debug("Debugging messages are enabled.")
    compile.compile_site(source_dir, output_dir, template_dir)


if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="[{asctime:s}] {message:s}",
        style="{",
        datefmt="%y-%m-%d %H:%M:%S",
    )
    _show_cli()
