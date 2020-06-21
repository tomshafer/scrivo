"""Command-line interface to the website generation tool."""
import logging
from argparse import ArgumentParser, Namespace
from time import time

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
        "-s",
        metavar="<source_dir>",
        dest="SOURCE_DIR",
        required=True,
        help="source directory (root of the website source)",
    )
    parser.add_argument(
        "-o",
        metavar="<output_dir>",
        dest="OUTPUT_DIR",
        required=True,
        help="output directory (root of the compiled website)",
    )
    parser.add_argument(
        "-c",
        metavar="<config_yml>",
        dest="CONFIG_YAML",
        default="config.yml",
        help="location of the YAML configuration file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli = parse_args()
    if cli.VERBOSE:
        logging.getLogger().setLevel(logging.INFO)
    config = read_config(cli.CONFIG_YAML)
    time_start = time()
    compile_site(
        source_dir=cli.SOURCE_DIR,
        build_dir=cli.OUTPUT_DIR,
        config=config,
        include_drafts=cli.INCLUDE_DRAFTS,
    )
    logging.info("finished compilation in %.3f seconds", time() - time_start)
