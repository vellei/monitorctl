import argparse
import json
import logging
import structlog

from argparse import Namespace

from monitorctl.hypr_v1 import HyprV1Socket, HyprV1Command
from monitorctl.config import Config

logger = structlog.get_logger()


def main():
    parser = argparse.ArgumentParser()
    parsers = []

    subparser = parser.add_subparsers(title="Subcommands", required=True)
    update_parser = subparser.add_parser(
        "update",
        description="Update the existing config based on current connected hardware",
    )
    update_parser.add_argument("config", help="Path to workspace config rules")
    update_parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Print changes to configs to stdout instead of overwriting the files",
    )
    update_parser.add_argument("-y", "--hypr", type=str, help="Path to hyprland config")
    update_parser.add_argument("-w", "--waybar", type=str, help="Path to config config")
    update_parser.set_defaults(action=run_update)
    parsers.append(update_parser)

    monitor_info_parser = subparser.add_parser(
        "monitor-info", description="Get current monitor information"
    )
    monitor_info_parser.set_defaults(action=run_monitor_info)
    parsers.append(monitor_info_parser)

    # Define common arguments for every subcommand
    for p in parsers:
        group = p.add_mutually_exclusive_group()
        group.add_argument(
            "-q", "--quiet", action="store_true", help="Disable all logging"
        )
        group.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose logging",
        )

    args = parser.parse_args()

    # Determine logging level
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.ERROR
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(level))

    # Invoke subcommands
    args.action(args)


def run_monitor_info(args: Namespace):
    socket = HyprV1Socket()
    print(json.dumps(socket.get_monitors(), indent=4))


def run_update(args: Namespace):
    socket = HyprV1Socket()

    config = Config.parse(args.config)
    current_monitors = socket.get_monitors()

    for monitor in config.monitors:
        logger.info("Current monitor", config=monitor)
