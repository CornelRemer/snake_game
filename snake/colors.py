from enum import Enum
from typing import List, Tuple


class RGBColorCode(Enum):
    WHITE: Tuple[int, ...] = (255, 255, 255)
    RED: Tuple[int, ...] = (255, 102, 102)
    DARKGREY: Tuple[int, ...] = (64, 64, 64)
    GREEN: Tuple[int, ...] = (102, 255, 102)

    @classmethod
    def get_color_names(cls) -> List[str]:
        return [color.name for color in cls]
