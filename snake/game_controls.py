from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Optional

from snake.pygame_interface.constants import (
    PYGAME_K_DOWN,
    PYGAME_K_LEFT,
    PYGAME_K_RIGHT,
    PYGAME_K_UP,
    PYGAME_KEYDOWN,
    PYGAME_QUIT,
)
from snake.pygame_interface.utils import get_pygame_events


class Direction(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()


class AbstractEventHandler(ABC):
    @abstractmethod
    def handle_events(self) -> None:
        pass

    @abstractmethod
    def get_updated_direction(self) -> Optional[Direction]:
        pass

    @abstractmethod
    def quit_game(self) -> bool:
        pass


# ToDo: remove key exception when pressing any key!!
class PygameEventHandler(AbstractEventHandler):
    def __init__(self):
        self._events = []
        self._direction: Optional[Direction] = None
        self._quit_game: bool = False

    def handle_events(self) -> None:
        self._update_events()
        self._handle_game_quit_event()
        self._handle_user_input_events()

    def _update_events(self) -> None:
        self._events = get_pygame_events()

    def _handle_game_quit_event(self) -> None:
        for event in self._events:
            if event.type == PYGAME_QUIT:
                self._quit_game = True

    def _handle_user_input_events(self) -> None:
        for event in self._events:
            if event.type == PYGAME_KEYDOWN:
                self._direction = self._event_key_registry[event.key]

    @property
    def _event_key_registry(self) -> Dict[int, Direction]:
        return {
            PYGAME_K_LEFT: Direction.LEFT,
            PYGAME_K_RIGHT: Direction.RIGHT,
            PYGAME_K_UP: Direction.UP,
            PYGAME_K_DOWN: Direction.DOWN,
        }

    def get_updated_direction(self) -> Optional[Direction]:
        return self._direction

    def quit_game(self) -> bool:
        return self._quit_game
