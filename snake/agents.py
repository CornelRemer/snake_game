from abc import ABC, abstractmethod
from typing import Dict, List

from snake.game import SnakeGame, SnakeGameFactory
from snake.game_controls import PygameEventHandler
from snake.game_objects.objects import Point
from snake.publisher import ScoreSubscriber


class AbstractAgent(ABC):
    @abstractmethod
    def play_game(self) -> None:
        pass

    @abstractmethod
    def restart_game(self) -> None:
        pass

    def wants_to_play(self) -> bool:
        pass


class UserAgent(AbstractAgent):
    def __init__(self, game_factory: SnakeGameFactory):
        self._game_factory = game_factory
        self._game = self._game_factory.create_snake_game()

        self._state = {"score": 0}
        self._subscriber = ScoreSubscriber(state=self._state)
        self._game.add_subscriber(self._subscriber)

        self._event_handler = PygameEventHandler()

    def play_game(self) -> None:
        self._gather_user_input_and_set_new_direction()
        self._game.run()

    def _gather_user_input_and_set_new_direction(self) -> None:
        self._event_handler.handle_events()
        new_direction = self._event_handler.get_updated_direction()
        self._game.update_direction(new_direction)

    def wants_to_play(self) -> bool:
        if self._game.is_over() or self._event_handler.quit_game():
            if self._user_want_to_restart():
                self.restart_game()
            else:
                return False
        return True

    def _user_want_to_restart(
        self,
    ) -> bool:
        print("Wanna play again? (y/n)")
        answer = str(input())
        return self._actions.get(answer, False)

    def restart_game(self) -> None:
        self._game = self._game_factory.create_snake_game()
        self._state = {"score": 0}
        self._subscriber = ScoreSubscriber(state=self._state)
        self._game.add_subscriber(self._subscriber)

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

    def get_score(self) -> int:
        return self._state["score"]
