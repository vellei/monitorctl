import json
import os
import structlog

from .program import Program

logger = structlog.get_logger()


class Waybar(Program):
    def __init__(self, path: str = None):
        default_path = os.path.join(os.environ["HOME"], ".config/waybar/config.jsonc")
        self.path = default_path if path is None else path

    def update(items: List | Dict):
        waybar = self.config()
        w = waybar.get("hyprland/workspaces")
        w.update({"persistent-workspaces": items})
        with open(self.path, "w") as f:
            f.write(waybar)

    def config() -> Iterable:
        with open(self.path, "r") as f:
            try:
                waybar = json.load(f)
            except Exception as e:
                raise e
            if waybar is None or waybar == {}:
                logger.error("Failed to read waybar config")
                return
            return waybar
