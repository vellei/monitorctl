import argparse
import structlog

from argparse import Namespace

log = structlog.get_logger()


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title="Subcommands", required=True)

    update_parser = subparser.add_parser(
        "update",
        description="Update the existing config based on current connected hardware",
    )
    update_parser.add_argument("-c", "--config", help="Path to workspace config rules")
    update_parser.set_defaults(action=run_update)

    info_parser = subparser.add_parser(
        "info", description="Get current monitor information"
    )
    info_parser.set_defaults(action=run_info)
    args = parser.parse_args()
    args.action(args)


def run_info(args: Namespace):
    pass


def run_update(args: Namespace):
    pass
