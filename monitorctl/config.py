"""
hyprctl monitors -j | jq -r '.[] | { name: .name, description: .description, id: .id, serial: .serial, x: .x, y: .y}'
"""

import json
import os

from pydantic import BaseModel
from typing import List


class Workspace(BaseModel):
    name: str

    number: int


class Position(BaseModel):
    x: int

    y: int


class Config(BaseModel):
    serial: str

    name: str

    workspaces: List[Workspace]

    position: Position

    @staticmethod
    def parse(path: str) -> Config:
        assert os.path.exists(os.path.abspath(path)), "Config path does not exist"
        with open(path, "r") as f:
            data = json.load(f)
            return Config(**data)


# TODO: Unittests
