import random
from abc import ABC, abstractmethod
from collections import deque
from enum import Enum
from typing import Dict, List, Optional, cast

import numpy as np
import torch

from snake.config import GameConfig, WindowConfig
from snake.game import SnakeGame, SnakeGameFactory
from snake.game_controls import Direction, PygameEventHandler
from snake.game_objects.objects import Point
from snake.model import LinearQNet, QTrainer
from snake.publisher import (
    AbstractSubscriber,
    NoCollisionSubscriber,
    RewardSubscriber,
    ScoreSubscriber,
)
from snake.state import State, StateFactory


class Actions(Enum):
    STRAIGHT = [1, 0, 0]
    RIGHT_TURN = [0, 1, 0]
    LEFT_TURN = [0, 0, 1]


class Agents(Enum):
    UserAgent = "UserAgent"
    AIAgent = "AIAgent"

    @classmethod
    def get_agent_names(cls) -> List[str]:
        return [color.name for color in cls]


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

    @abstractmethod
    def get_max_score(self) -> int:
        pass


class UserAgent(AbstractAgent):
    def __init__(self, game_factory: SnakeGameFactory):
        self._game_factory = game_factory
        self._game = self._game_factory.create_snake_game()

        self._remuneration = self._initial_remuneration
        self._register_subscriber(self._initial_subscribers)

        self._event_handler = PygameEventHandler()
        self._max_score = 0

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
                self._increase_max_score()
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

    def _increase_max_score(self):
        new_score = self._remuneration["score"]
        if new_score > self._max_score:
            self._max_score = new_score

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

    def get_max_score(self) -> int:
        return self._max_score


class AIAgent(AbstractAgent):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, game_factory: SnakeGameFactory, state_factory: StateFactory):
        self._game_factory = game_factory
        self._game = self._game_factory.create_snake_game()

        self._remuneration = self._initial_remuneration
        self._register_subscriber(self._initial_subscribers)

        self._event_handler = PygameEventHandler()
        self._state_factory = state_factory
        self._state = self._state_factory.create_state_for_game(game=self._game)

        self._memory: deque = deque(maxlen=100_000)
        self._direction_store: deque = deque([0 for _ in range(9)], maxlen=9)
        self._n_games = 0
        self._epsilon = 0

        self._model = LinearQNet(input_feature_size=20, hidden_layer_size=256, output_feature_size=3)
        self._trainer = QTrainer(model=self._model, learning_rate=0.001, discount_rate=0.9)
        self._max_score = 0

    @property
    def _initial_remuneration(self) -> Dict[str, int]:
        return {"score": 0, "reward": 0}

    @property
    def _initial_subscribers(self) -> List[AbstractSubscriber]:
        return [
            ScoreSubscriber(remuneration=self._remuneration),
            RewardSubscriber(remuneration=self._remuneration),
            NoCollisionSubscriber(remuneration=self._remuneration),
        ]

    def _register_subscriber(self, subscribers: List[AbstractSubscriber]) -> None:
        for subscriber in subscribers:
            self._game.add_subscriber(subscriber)

    def play_game(self) -> None:
        self._event_handler.handle_events()
        self._store_direction()
        old_state = self._state.calculate_state_from_game()
        old_state = np.append(old_state, self._direction_store)

        action = self._get_actions(state=old_state)
        new_direction = self._convert_actions_to_directions(action)
        self._game.update_direction(new_direction)
        self._game.run()
        reward = self.get_reward()
        game_over = self._game.is_over()

        self._store_direction()
        new_state = self._state.calculate_state_from_game()
        new_state = np.append(new_state, self._direction_store)

        self._train_short_memory(
            old_state=old_state, action=action, reward=reward, new_state=new_state, is_game_over=game_over
        )
        self._remember(old_state=old_state, action=action, reward=reward, new_state=new_state, is_game_over=game_over)

    def _get_actions(self, state: State) -> Actions:
        self._epsilon = 80 - self._n_games
        action = [0, 0, 0]
        if random.randint(0, 200) < self._epsilon:
            move = random.randint(0, 2)
            action[move] = 1
        else:
            state_0 = torch.tensor(state, dtype=torch.float)
            prediction = self._model(state_0)
            move = cast(int, torch.argmax(prediction).item())
            action[move] = 1
        return Actions(action)

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

    def _store_direction(self) -> None:
        direction_as_binary = self._state.convert_direction_to_binary()
        self._direction_store.extend(direction_as_binary)

    def _train_short_memory(
        self, old_state: List[int], action: Actions, reward: int, new_state: List[int], is_game_over: bool
    ):
        action_value = cast(List[int], action.value)
        self._trainer.train_step(
            old_state=old_state, action=action_value, reward=reward, new_state=new_state, game_over=is_game_over
        )

    def _remember(self, old_state: List[int], action: Actions, reward: int, new_state: List[int], is_game_over: bool):
        action_value = cast(List[int], action.value)
        self._memory.append((old_state, action_value, reward, new_state, is_game_over))

    def wants_to_play(self) -> bool:
        if self._event_handler.quit_game():
            return False
        if self._game.is_over():
            self._increase_max_score()
            self.restart_game()
            self._state = self._state_factory.create_state_for_game(game=self._game)
            self._n_games += 1
            self._train_long_memory()
            self._model.save()
        return True

    def _increase_max_score(self):
        new_score = self._remuneration["score"]
        if new_score > self._max_score:
            self._max_score = new_score

    def restart_game(self) -> None:
        self._game = self._game_factory.create_snake_game()
        self._remuneration = self._initial_remuneration
        self._register_subscriber(self._initial_subscribers)

    def _train_long_memory(self):
        batch_size = 1_000
        if len(self._memory) > batch_size:
            mini_sample = random.sample(self._memory, batch_size)
        else:
            mini_sample = self._memory

        old_states, actions, rewards, new_states, game_overs = zip(*mini_sample)
        self._trainer.train_step(
            old_state=old_states, action=actions, reward=rewards, new_state=new_states, game_over=game_overs
        )

    @property
    def game(self) -> SnakeGame:
        return self._game

    def get_snake(self) -> List[Point]:
        return self._game.get_snake()

    def get_score(self) -> int:
        return self._remuneration["score"]

    def get_max_score(self) -> int:
        return self._max_score

    def get_reward(self) -> int:
        return self._remuneration["reward"]


class AgentFactory(ABC):
    def __init__(self, window_configuration: WindowConfig, game_configuration: GameConfig):
        self._window_config = window_configuration
        self._game_config = game_configuration

    @abstractmethod
    def create_agent(self) -> AbstractAgent:
        pass


class AbstractAgentFactory(AgentFactory):
    def __init__(
        self, window_configuration: WindowConfig, game_configuration: GameConfig, agent_type: Optional[Agents] = None
    ):
        self._agent_type = agent_type or Agents(game_configuration.agent_type)
        super().__init__(window_configuration=window_configuration, game_configuration=game_configuration)

    def create_agent(self) -> AbstractAgent:
        return cast(
            AbstractAgent,
            self._available_agents[self._agent_type](
                window_configuration=self._window_config, game_configuration=self._game_config
            ).create_agent(),
        )

    @property
    def _available_agents(self) -> Dict:
        return {
            Agents.UserAgent: UserAgentFactory,
            Agents.AIAgent: AIAgentFactory,
        }


class UserAgentFactory(AgentFactory):
    def create_agent(self) -> UserAgent:
        return UserAgent(
            SnakeGameFactory(window_configuration=self._window_config, game_configuration=self._game_config)
        )


class AIAgentFactory(AgentFactory):
    def create_agent(self) -> AIAgent:
        return AIAgent(
            game_factory=SnakeGameFactory(
                window_configuration=self._window_config, game_configuration=self._game_config
            ),
            state_factory=StateFactory(game_configuration=self._game_config),
        )
