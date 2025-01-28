import json
import os

from pydantic import BaseModel
from typing import List


class Workspace(BaseModel):
    """
    Defines the workspace attached to a monitor
    """

    name: str
    """
    A string to use when representing this workspace
    """

    number: int
    """
    The workspace index, used when creating keybinds and order the appearance of
    workspaces
    """


class Position(BaseModel):
    """
    Position of the monitor
    """

    x: int

    y: int


class Monitor(BaseModel):
    """
    Defines a monitor's configuration
    """

    serial: str
    """
    Serial number of this monitor that can be found via monitorctl or hyprctl
    """

    name: str
    """
    A human-readable name for this monitor (currently unused by monitorctl)
    """

    workspaces: List[Workspace]
    """
    The workspaces bound to this monitor
    """

    position: Position
    """
    The absolute position of this monitor
    """


class Config(BaseModel):
    """
    A config that describes which workspaces are bound to each monitor. Use to
    configure hyprland and waybar
    """

    monitors: List[Monitor]

    @staticmethod
    def parse(path: str) -> "Config":
        """
        Parse and validate a monitorctl config
        """
        assert os.path.exists(os.path.abspath(path)), "Config path does not exist"
        with open(path, "r") as f:
            data = json.load(f)
            return Config(**data)


# TODO: Unittests
