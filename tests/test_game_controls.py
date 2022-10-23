from typing import List
from unittest.mock import patch

import pytest
from pygame.constants import K_DOWN, K_LEFT, K_RIGHT, K_UP, KEYDOWN, QUIT
from pygame.event import Event as PyEvent

from snake.game_controls import Direction, PygameEventHandler


class TestPygameEventHandler:
    def test_handle_events_for_quit_event(self):
        fake_input_events = [PyEvent(QUIT)]
        with patch(target="snake.game_controls.get_pygame_events") as mocked_pygame_events:
            mocked_pygame_events.return_value = fake_input_events
            event_handler = PygameEventHandler()
            assert not event_handler.quit_game()

            event_handler.handle_events()
            assert event_handler.quit_game()

    @pytest.mark.parametrize(
        "fake_input_event, expected_direction",
        [
            ([PyEvent(KEYDOWN, key=K_RIGHT)], Direction.RIGHT),
            ([PyEvent(KEYDOWN, key=K_LEFT)], Direction.LEFT),
            ([PyEvent(KEYDOWN, key=K_UP)], Direction.UP),
            ([PyEvent(KEYDOWN, key=K_DOWN)], Direction.DOWN),
        ],
        ids=[
            "KEYDOWN event right key",
            "KEYDOWN event left key",
            "KEYDOWN event up key",
            "KEYDOWN event down key",
        ],
    )
    def test_get_updated_direction_for_keydown_event(
        self, fake_input_event: List[PyEvent], expected_direction: Direction
    ):
        with patch(target="snake.game_controls.get_pygame_events") as mocked_pygame_events:
            mocked_pygame_events.return_value = fake_input_event
            event_handler = PygameEventHandler()
            event_handler.handle_events()
            actual_direction = event_handler.get_updated_direction()
            assert actual_direction == expected_direction
