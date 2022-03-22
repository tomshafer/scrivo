"""Command-line interface to the website generation tool."""
import logging
from argparse import ArgumentParser, Namespace

from scrivo.build import compile_site
from scrivo.config import read_config


def parse_args() -> Namespace:
    """Provide a command-line interface to the tool."""
    parser = ArgumentParser(prog="scrivo.py")
    parser.add_argument(
        "-v",
        action="store_true",
        dest="VERBOSE",
        help="display runtime information during build",
    )
    parser.add_argument(
        "--drafts",
        action="store_true",
        dest="INCLUDE_DRAFTS",
        help="compile drafts in addition to finalized posts",
    )
    parser.add_argument(
        "-c",
        metavar="<config_yml>",
        dest="CONFIG_YAML",
        default="config.yml",
        required=True,
        help="location of the YAML configuration file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli = parse_args()
    if cli.VERBOSE:
        logging.getLogger().setLevel(logging.INFO)
    config = read_config(cli.CONFIG_YAML)
    # FIXME: Combine CLI args with config in a sensible way
    compile_site(
        source_dir=config.site.source_dir,
        build_dir=config.site.build_dir,
        config=config,
        include_drafts=cli.INCLUDE_DRAFTS,
    )
