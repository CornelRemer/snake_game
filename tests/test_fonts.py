import pytest
from pygame.font import Font

from snake.fonts import MAX_FONT_SIZE, MIN_FONT_SIZE, Arial, FontException


class TestArial:
    def test_font_type_is_correct(self):
        valid_font_size = 25
        actual_font = Arial(font_size=valid_font_size).font
        assert isinstance(actual_font, Font)

    @pytest.mark.parametrize(
        "invalid_font_size",
        (
            MIN_FONT_SIZE - 1,
            MAX_FONT_SIZE + 1,
        ),
        ids=[
            "Font size to small",
            "Font size to large",
        ],
    )
    def test_raise_exception_for_invalid_font_size(self, invalid_font_size):
        with pytest.raises(FontException):
            Arial(font_size=invalid_font_size)
