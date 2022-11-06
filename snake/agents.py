import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List

import numpy as np

from snake.game import SnakeGame, SnakeGameFactory
from snake.game_controls import Direction, PygameEventHandler
from snake.game_objects.objects import Point
from snake.publisher import AbstractSubscriber, RewardSubscriber, ScoreSubscriber


class Actions(Enum):
    STRAIGHT = [1, 0, 0]
    RIGHT_TURN = [0, 1, 0]
    LEFT_TURN = [0, 0, 1]


class AbstractAgent(ABC):
    @abstractmethod
    def play_game(self) -> None:
        pass

    @abstractmethod
    def restart_game(self) -> None:
        pass

    @abstractmethod
    def wants_to_play(self) -> bool:
        pass

    @abstractmethod
    def get_score(self) -> int:
        pass


class UserAgent(AbstractAgent):
    def __init__(self, game_factory: SnakeGameFactory):
        self._game_factory = game_factory
        self._game = self._game_factory.create_snake_game()

        self._remuneration = self._initial_remuneration
        self._register_subscriber(self._initial_subscribers)

        self._event_handler = PygameEventHandler()

    @property
    def _initial_remuneration(self) -> Dict[str, int]:
        return {"score": 0}

    @property
    def _initial_subscribers(self) -> List[AbstractSubscriber]:
        return [ScoreSubscriber(remuneration=self._remuneration)]

    def _register_subscriber(self, subscribers: List[AbstractSubscriber]) -> None:
        for subscriber in subscribers:
            self._game.add_subscriber(subscriber)

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
        self._remuneration = self._initial_remuneration
        self._register_subscriber(self._initial_subscribers)

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
        return self._remuneration["score"]


class AIAgent(AbstractAgent):
    def __init__(self, game_factory: SnakeGameFactory):
        self._game_factory = game_factory
        self._game = self._game_factory.create_snake_game()

        self._remuneration = self._initial_remuneration
        self._register_subscriber(self._initial_subscribers)

        self._event_handler = PygameEventHandler()

    @property
    def _initial_remuneration(self) -> Dict[str, int]:
        return {"score": 0, "reward": 0}

    @property
    def _initial_subscribers(self) -> List[AbstractSubscriber]:
        return [ScoreSubscriber(remuneration=self._remuneration), RewardSubscriber(remuneration=self._remuneration)]

    def _register_subscriber(self, subscribers: List[AbstractSubscriber]) -> None:
        for subscriber in subscribers:
            self._game.add_subscriber(subscriber)

    def play_game(self) -> None:
        self._event_handler.handle_events()
        action = self._get_actions()
        new_direction = self._convert_actions_to_directions(action)
        self._game.update_direction(new_direction)
        self._game.run()

    @staticmethod
    def _get_actions() -> Actions:
        # get actions from model
        return random.choice([Actions.STRAIGHT, Actions.RIGHT_TURN, Actions.LEFT_TURN])

    def _convert_actions_to_directions(self, action: Actions) -> Direction:
        clock_wise_directions = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise_directions.index(self._game.get_current_direction())
        if np.array_equal(action.value, Actions.STRAIGHT.value):
            new_direction = clock_wise_directions[idx]
        elif np.array_equal(action.value, Actions.RIGHT_TURN.value):
            next_idx = (idx + 1) % 4
            new_direction = clock_wise_directions[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_direction = clock_wise_directions[next_idx]

        return new_direction

    def wants_to_play(self) -> bool:
        if self._event_handler.quit_game():
            return False
        if self._game.is_over():
            self.restart_game()
        return True

    def restart_game(self) -> None:
        self._game = self._game_factory.create_snake_game()
        self._remuneration = self._initial_remuneration
        self._register_subscriber(self._initial_subscribers)

    @property
    def game(self) -> SnakeGame:
        return self._game

    def get_snake(self) -> List[Point]:
        return self._game.get_snake()

    def get_score(self) -> int:
        return self._remuneration["score"]

    def get_reward(self) -> int:
        return self._remuneration["reward"]
