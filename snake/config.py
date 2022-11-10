from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, cast

from dynaconf import Validator

from snake.colors import RGBColorCode
from snake.dynaconf_config import settings


@dataclass
class WindowConfig:
    HEIGHT_VALIDATOR = Validator("height", is_type_of=int, gt=0, must_exist=True)
    WIDTH_VALIDATOR = Validator("width", is_type_of=int, gt=0, must_exist=True)
    BACKGROUND_COLOR_VALIDATOR = Validator(
        "background_color", is_type_of=str, is_in=RGBColorCode.get_color_names(), default="BLACK"
    )
    FONT_COLOR_VALIDATOR = Validator(
        "background_color", is_type_of=str, is_in=RGBColorCode.get_color_names(), default="WHITE"
    )
    height: int
    width: int
    background_color: Tuple[int, int, int]
    font_color: Tuple[int, int, int]

    @staticmethod
    def from_dynaconf() -> WindowConfig:
        return WindowConfig(
            height=settings.get("height"),
            width=settings.get("width"),
            background_color=cast(Tuple[int, int, int], RGBColorCode[settings.get("background_color")].value),
            font_color=cast(Tuple[int, int, int], RGBColorCode[settings.get("font_color")].value),
        )

    @classmethod
    def get_all_validators(cls) -> List[Validator]:
        return [
            cls.HEIGHT_VALIDATOR,
            cls.WIDTH_VALIDATOR,
            cls.BACKGROUND_COLOR_VALIDATOR,
            cls.FONT_COLOR_VALIDATOR,
        ]


@dataclass
class GameConfig:
    # pylint: disable=too-many-instance-attributes
    FRAME_RATE_VALIDATOR = Validator("frame_rate", is_type_of=int, gt=0, must_exist=True)
    START_LENGTH_VALIDATOR = Validator("start_length", is_type_of=int, gt=0, must_exist=True)
    OUTER_BLOCK_SIZE_VALIDATOR = Validator("outer_block_size", is_type_of=int, gt=0, must_exist=True)
    INNER_BLOCK_SIZE_VALIDATOR = Validator("inner_block_size", is_type_of=int, gt=0, must_exist=True)
    OUTER_BLOCK_COLOR_VALIDATOR = Validator(
        "outer_block_color", is_type_of=str, is_in=RGBColorCode.get_color_names(), default="DARKBLUE"
    )
    INNER_BLOCK_COLOR_VALIDATOR = Validator(
        "inner_block_color", is_type_of=str, is_in=RGBColorCode.get_color_names(), default="LIGHTBLUE"
    )
    FOOD_COLOR_VALIDATOR = Validator("food_color", is_type_of=str, is_in=RGBColorCode.get_color_names(), default="RED")
    AGENT_TYPE_VALIDATOR = Validator("agent_type", is_type_of=str, is_in=["UserAgent", "AIAgent"], default="AIAgent")

    frame_rate: int
    start_length: int
    outer_block_size: int
    inner_block_size: int
    outer_block_color: Tuple[int, int, int]
    inner_block_color: Tuple[int, int, int]
    food_color: Tuple[int, int, int]
    agent_type: str

    @staticmethod
    def from_dynaconf() -> GameConfig:
        return GameConfig(
            frame_rate=settings.get("frame_rate"),
            start_length=settings.get("start_length"),
            outer_block_size=settings.get("outer_block_size"),
            inner_block_size=settings.get("inner_block_size"),
            outer_block_color=cast(Tuple[int, int, int], RGBColorCode[settings.get("outer_block_color")].value),
            inner_block_color=cast(Tuple[int, int, int], RGBColorCode[settings.get("inner_block_color")].value),
            food_color=cast(Tuple[int, int, int], RGBColorCode[settings.get("food_color")].value),
            agent_type=settings.get("agent_type"),
        )

    @classmethod
    def get_all_validators(cls) -> List[Validator]:
        return [
            cls.FRAME_RATE_VALIDATOR,
            cls.START_LENGTH_VALIDATOR,
            cls.OUTER_BLOCK_SIZE_VALIDATOR,
            cls.INNER_BLOCK_SIZE_VALIDATOR,
            cls.OUTER_BLOCK_COLOR_VALIDATOR,
            cls.INNER_BLOCK_COLOR_VALIDATOR,
            cls.FOOD_COLOR_VALIDATOR,
            cls.AGENT_TYPE_VALIDATOR,
        ]
