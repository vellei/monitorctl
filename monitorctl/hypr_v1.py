import json
import os
import socket
import structlog

from enum import StrEnum
from typing import Dict, List


class HyprV1Command(StrEnum):
    """
    Represents possible commands that the hypr v1 socket accepts this is the
    same as hyprctl(1)
    """

    ACTIVE_WINDOW = "activewindow"
    """
    Gets the active window name and its properties
    """

    ACTIVE_WORKSPACE = "activeworkspace"
    """
    Gets the active workspace and its properties
    """

    ANIMATIONS = "animations"
    """
    Get the current configured info abou animations and beziers
    """

    BINDS = "binds"
    """
    List all registered binds
    """

    CLIENTS = "clients"
    """
    List all windows with their current properties
    """

    CONFIG_ERRORS = "configerrors"
    """
    List all current config parsing errors
    """

    CURSOR_POS = "cursorpos"
    """
    Gets th current cursor position in global layout coordinates
    """

    DECORATIONS = "decorations"
    """
    List all decorations and their info
    """

    DEVICES = "devices"
    """
    Lists all connected keyboards and mice
    """

    DISMISS_NOTIFY = "dismissnotify"
    """
    Dismisses all or up to AMOUNT notifications
    """

    DISPATCH = "dispatch"
    """
    Issue a dispatch to call a keybind dispatcher with arguments
    """

    GET_OPTION = "getoption"
    """
    Gets the config option status (values)
    """

    GLOBAL_SHORTCUTS = "globalshortcuts"
    """
    Lists all global shortcuts
    """

    HYPR_PAPER = "hyprpaper"
    """
    Issue a hyprpaper request
    """

    INSTANCES = "instances"
    """
    Lists all running instances of Hyprland with their info
    """

    KEYWORD = "keyword"
    """
    Issue a keyword to call a config keyword dynamically
    """

    KILL = "kill"
    """
    Issue a kill to get into a kill mode, where you can kill an app by clicking on
    it. You can exit it with ESCAPE
    """

    LAYERS = "layers"
    """
    Lists all the surface layers
    """

    LAYOUTS = "layouts"
    """
    Lists all layouts available (including plugin'd ones)
    """

    MONITORS = "monitors"
    """
    Lists active outputs with their properties, 'monitors all' lists active and
    inactive outputs
    """

    NOTIFY = "notify"
    """
    Sends a notification using the built-in Hyprland notification system
    """

    OUTPUT = "output"
    """
    Allows you to add and remove fake outputs to your preferred backend
    """

    PLUGIN = "plugin"
    """
    Issue a plugin request 
    """

    RELOAD = "reload"
    """
    Issue a reload to force reload the config. Pass 'config-only' to disable
    monitor reload
    """

    ROLLING_LOG = "rollinglog"
    """
    Prints tail of the log. Also supports -f/--follow option 
    """

    SET_CURSOR = "setcursor"
    """
    Sets the cursor theme and reloads the cursor manager 
    """

    SET_ERROR = "seterror"
    """
    Sets the hyprctl error string. Color has the same format as in colors in config.
    Will reset when Hyprland's config is reloaded
    """

    SET_PROP = "setprop"
    """
    Sets a window property 
    """

    SPLASH = "splash"
    """
    Get the current splash
    """

    SWITCH_XKB_LAYOUT = "switchxkblayout"
    """
    Sets the xkb layout index for a keyboard 
    """

    SYSTEM_INFO = "systeminfo"
    """
    Get system info
    """

    VERSION = "version"
    """
    Print the hyprland version, meaning flags, commit and branch of build
    """

    WORKSPACE_RULES = "workspacerules"
    """
    Lists all workspace rules 
    """

    WORKSPACES = "workspaces"
    """
    Lists all workspaces with their properties 
    """

    def command(self, json: bool = True, refresh: bool = False, **kwargs) -> str:
        return f"-j/{self.value}" if json else self.value

    def bytes(self, json: bool = True, refresh: bool = False, **kwargs) -> bytes:
        return str.encode(f"-j/{self.value}") if json else str.encode(self.value)


class HyprV1Socket:
    BUFFER_SIZE = 4096

    def __init__(self, path: str = None):
        if path is None:
            xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
            instance = (
                "*"
                if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") is None
                else os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
            )
            assert xdg_runtime_dir, "XDG_RUNTIME_DIR is not set"
            assert os.path.exists(xdg_runtime_dir), "XDG_RUNTIME_DIR does not exist"
            self.path = os.path.join(xdg_runtime_dir, "hypr", instance, ".socket.sock")
        else:
            self.path = path

        assert os.path.exists(self.path), "Socket path does not exist"
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(self.path)

    def __repr__(self) -> str:
        return self.path

    def get_monitors(self) -> List[Dict]:
        """
        Retreive information about current set of monitors
        """
        m = []
        monitors = json.loads(self.send(HyprV1Command.MONITORS))
        for monitor in monitors:
            m.append(
                {
                    "name": monitor.get("name"),
                    "description": monitor.get("description"),
                    "serial": monitor.get("serial"),
                    "x": monitor.get("x"),
                    "y": monitor.get("y"),
                }
            )
        assert len(m) > 0, "Failed to find any connected monitors"
        return m

    def send(
        self, command: HyprV1Command, json: bool = True, refresh: bool = False
    ) -> str:
        """
        Sends a hyprctl(1) command to the hypr socket and returns the response
        """
        response = ""

        try:
            self.socket.send(command.bytes(json=json, refresh=refresh))
            while True:
                b = self.socket.recv(self.BUFFER_SIZE)
                if b:
                    response += b.decode("utf-8")
                else:
                    break
        except Exception as e:
            raise e

        assert len(response) > 0, "Received empty response from socket"
        assert response != "Unknown command", "Response indicates command was unknown"
        return response
