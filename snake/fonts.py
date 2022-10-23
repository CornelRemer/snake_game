from pygame.font import Font, SysFont

MAX_FONT_SIZE = 35
MIN_FONT_SIZE = 15


class FontException(Exception):
    pass


class Arial:
    def __init__(self, font_size: int, font_name: str = "arial"):
        if not self._valid_font_size(font_size):
            raise FontException(
                f"Invalid font size: {font_size}. "
                f"min font size: {MIN_FONT_SIZE}, "
                f"max font size: {MAX_FONT_SIZE}"
            )

        self._font_size = font_size
        self._font_name = font_name

    @staticmethod
    def _valid_font_size(font_size: int) -> bool:
        return MIN_FONT_SIZE <= font_size <= MAX_FONT_SIZE

    @property
    def font(self) -> Font:
        return SysFont(name=self._font_name, size=self._font_size)
