from abc import ABC, abstractmethod
from typing import Dict, List

from snake.config import GameConfig, WindowConfig
from snake.game import SnakeGame
from snake.game_controls import PygameEventHandler
from snake.game_objects.factories import (
    FoodFactory,
    FoodHandlerFactory,
    SnakeFactory,
    SnakeHandlerFactory,
)
from snake.game_objects.objects import Point


class AbstractAgent(ABC):
    def __init__(self, game: SnakeGame):
        self._game = game

    @abstractmethod
    def play_game(self) -> None:
        pass

    @abstractmethod
    def restart_game(self) -> None:
        pass

    def wants_to_play(self) -> bool:
        pass


class UserAgent(AbstractAgent):
    def __init__(self, game: SnakeGame, window_configuration: WindowConfig, game_configuration: GameConfig):
        self._window_config = window_configuration
        self._game_config = game_configuration
        self._event_handler = PygameEventHandler()
        super().__init__(game)

    def play_game(self) -> None:
        self._gather_user_input_and_set_new_direction()
        self._game.run()

    def _gather_user_input_and_set_new_direction(self) -> None:
        self._event_handler.handle_events()
        new_direction = self._event_handler.get_updated_direction()
        self._game.update_direction(new_direction)

    def restart_game(self) -> None:
        self._game = SnakeGame(
            window_config=self._window_config,
            game_config=self._game_config,
            snake_handler=SnakeHandlerFactory(
                snake=SnakeFactory(
                    window_config=self._window_config,
                    game_config=self._game_config,
                ).create_snake()
            ).create_snake_handler(),
            food_handler=FoodHandlerFactory(
                food=FoodFactory(window_config=self._window_config, game_config=self._game_config).create_food(),
                window_config=self._window_config,
            ).create_food_handler(),
        )

    def wants_to_play(self) -> bool:
        if self._game.is_over() or self._event_handler.quit_game():
            print("Wanna play again? (y/n)")
            answer = str(input())
            self.restart_game()
            return self._actions.get(answer, False)
        return True

    @property
    def _actions(self) -> Dict:
        return {
            "y": True,
            "n": False,
        }

    @property
    def game(self) -> SnakeGame:
        return self._game

    def get_snake(self) -> List[Point]:
        return self._game.get_snake()
