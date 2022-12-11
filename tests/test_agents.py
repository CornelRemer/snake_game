from enum import Enum, auto
from typing import List, Optional
from unittest.mock import patch

import pytest

from snake.agents import Actions, AIAgentFactory, UserAgent
from snake.config import GameConfig, WindowConfig
from snake.game import SnakeGameFactory
from snake.game_controls import AbstractEventHandler, Direction
from snake.game_objects.objects import Point


class FakeEvents(Enum):
    QUIT = auto()
    LEFT = Direction.LEFT
    RIGHT = Direction.RIGHT
    UP = Direction.UP
    DOWN = Direction.DOWN


class FakeEventHandler(AbstractEventHandler):
    def __init__(self):
        self._events = []
        self._direction: Optional[Direction] = None
        self._quit_game: bool = False

    def handle_events(self) -> None:
        for event in self._events:
            if event == FakeEvents.QUIT:
                self._quit_game = True
            elif event in (FakeEvents.LEFT, FakeEvents.RIGHT, FakeEvents.UP, FakeEvents.DOWN):
                self._direction = event.value
        self._events = []

    def add_test_events(self, events: List) -> None:
        self._events.extend(events)

    def get_updated_direction(self) -> Optional[Direction]:
        return self._direction

    def quit_game(self) -> bool:
        return self._quit_game


@pytest.fixture(name="snake_game_factory")
def fixture_snake_game_factory(window_config: WindowConfig, game_config: GameConfig) -> SnakeGameFactory:
    return SnakeGameFactory(window_configuration=window_config, game_configuration=game_config)


@pytest.fixture(name="fake_event_handler")
def fixture_fake_event_handler() -> FakeEventHandler:
    return FakeEventHandler()


@patch("snake.game.GameUI")
class TestUserAgent:
    # pylint: disable=too-many-arguments
    @pytest.mark.parametrize(
        "users_input, expected_answer",
        [
            ("y", True),
            ("n", False),
            ("invalid_input", False),
        ],
        ids=[
            "User wants to continue and wrote 'y' -> game continues",
            "User doesn't want to continue and wrote 'n' -> game stops",
            "User wrote invalid input -> game stops",
        ],
    )
    def test_play_game_handles_user_input_on_game_end(
        self,
        _,
        users_input: str,
        expected_answer: bool,
        fake_event_handler: FakeEventHandler,
        snake_game_factory: SnakeGameFactory,
    ):
        fake_event = [FakeEvents.QUIT]
        fake_event_handler.add_test_events(fake_event)

        with (
            patch("snake.agents.PygameEventHandler", return_value=fake_event_handler),
            patch("snake.agents.input", return_value=users_input),
        ):
            agent = UserAgent(game_factory=snake_game_factory)
            agent.play_game()

            assert agent.wants_to_play() == expected_answer

    @pytest.mark.parametrize(
        "game_is_over, quit_game, users_input, expected_answer",
        (
            (True, False, "y", True),
            (True, False, "n", False),
            (True, True, "y", True),
            (True, True, "n", False),
            (False, False, "", True),
            (False, True, "y", True),
            (False, True, "n", False),
        ),
        ids=[
            "Game is over but user wants to play again.",
            "Game is over and user doesn't want to play again.",
            "Game is over, user quit game and want to play again.",
            "Game is over, user quit game and doesn't want to play again.",
            "Game is neither over or was quit, hence game will continue.",
            "User stopped but wants to play again.",
            "User stopped and doesn't want to play again.",
        ],
    )
    def test_wants_to_play(
        self,
        _,
        game_is_over: bool,
        quit_game: bool,
        users_input: str,
        expected_answer: bool,
        snake_game_factory: SnakeGameFactory,
    ):
        with (
            patch("snake.agents.SnakeGame.is_over", return_value=game_is_over),
            patch("snake.agents.PygameEventHandler.quit_game", return_value=quit_game),
            patch("snake.agents.input", return_value=users_input),
        ):
            agent = UserAgent(game_factory=snake_game_factory)

            assert agent.wants_to_play() == expected_answer

    def test_restart_game_gets_called_if_agent_wants_to_play_again(
        self,
        _,
        snake_game_factory: SnakeGameFactory,
    ):
        with (
            patch("snake.agents.SnakeGame.is_over", return_value=True),
            patch("snake.agents.input", return_value="y"),
            patch("snake.agents.UserAgent.restart_game") as mocked_restart_game,
        ):
            agent = UserAgent(game_factory=snake_game_factory)
            agent.play_game()

            assert agent.wants_to_play()
            assert mocked_restart_game.call_count == 1

    def test_reset_game_creates_new_game_instance(
        self,
        _,
        snake_game_factory: SnakeGameFactory,
    ):
        with patch("snake.agents.SnakeGameFactory.create_snake_game") as mocked_create_snake_game:
            agent = UserAgent(game_factory=snake_game_factory)
            agent.restart_game()

            assert mocked_create_snake_game.call_count == 2

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "input_event, expected_snake",
        (
            ([], [Point(x=55, y=25), Point(x=50, y=25), Point(x=45, y=25)]),
            ([FakeEvents.RIGHT], [Point(x=55, y=25), Point(x=50, y=25), Point(x=45, y=25)]),
            ([FakeEvents.UP], [Point(x=50, y=20), Point(x=50, y=25), Point(x=45, y=25)]),
            ([FakeEvents.DOWN], [Point(x=50, y=30), Point(x=50, y=25), Point(x=45, y=25)]),
        ),
        ids=[
            "no input from user -> snake has to move to the right side (default)",
            "input 'right' from user -> snake has to move to the right side",
            "input 'up' from user -> snake has to move up",
            "input 'down' from user -> snake has to move down",
        ],
    )
    def test_play_game_with_user_input_moves_snake_correctly(
        self,
        _,
        input_event: List[Optional[FakeEvents]],
        expected_snake: List[Point],
        fake_event_handler: FakeEventHandler,
        snake_game_factory: SnakeGameFactory,
    ):
        fake_event_handler.add_test_events(input_event)

        with patch("snake.agents.PygameEventHandler", return_value=fake_event_handler):
            agent = UserAgent(game_factory=snake_game_factory)
            agent.play_game()

            assert agent.get_snake() == expected_snake

    @pytest.mark.integration
    def test_run_snake_movement_for_multiple_inputs(
        self,
        _,
        fake_event_handler: FakeEventHandler,
        snake_game_factory: SnakeGameFactory,
    ):
        fake_events = [None, None, Direction.DOWN, None, Direction.LEFT, FakeEvents.QUIT]

        with (
            patch("snake.agents.PygameEventHandler", return_value=fake_event_handler),
            patch("snake.agents.input", return_value="n"),
        ):
            agent = UserAgent(game_factory=snake_game_factory)

            for fake_event in fake_events:
                fake_event_handler.add_test_events([fake_event])
                agent.play_game()

            assert agent.get_snake() == [Point(x=80, y=25), Point(x=75, y=25), Point(x=70, y=25)]
            assert not agent.wants_to_play()


@pytest.fixture(name="ai_agent_factory")
def fixture_ai_agent_factory(window_config: WindowConfig, game_config: GameConfig) -> AIAgentFactory:
    return AIAgentFactory(window_configuration=window_config, game_configuration=game_config)


@patch("snake.game.GameUI")
class TestAIAgent:
    # pylint: disable=too-many-arguments
    def test_play_game_handles_user_input_on_game_end(
        self,
        _,
        fake_event_handler: FakeEventHandler,
        ai_agent_factory: AIAgentFactory,
    ):
        fake_event = [FakeEvents.QUIT]
        fake_event_handler.add_test_events(fake_event)

        with patch("snake.agents.PygameEventHandler", return_value=fake_event_handler):
            agent = ai_agent_factory.create_agent()
            agent.play_game()

            assert not agent.wants_to_play()

    @pytest.mark.parametrize(
        "game_is_over, expected_answer",
        (
            (True, True),
            (False, True),
        ),
    )
    def test_wants_to_play(
        self,
        _,
        game_is_over: bool,
        expected_answer: bool,
        ai_agent_factory: AIAgentFactory,
    ):
        with (
            patch("snake.agents.SnakeGame.is_over", return_value=game_is_over),
            patch("snake.agents.AIAgent._train_long_memory"),
        ):
            agent = ai_agent_factory.create_agent()

            assert agent.wants_to_play() == expected_answer

    def test_restart_game_gets_called_if_agent_wants_to_play_again(
        self,
        _,
        ai_agent_factory: AIAgentFactory,
    ):
        with (
            patch("snake.agents.SnakeGame.is_over", return_value=True),
            patch("snake.agents.AIAgent.restart_game") as mocked_restart_game,
        ):
            agent = ai_agent_factory.create_agent()
            agent.play_game()

            assert agent.wants_to_play()
            assert mocked_restart_game.call_count == 1

    def test_reset_game_creates_new_game_instance(
        self,
        _,
        ai_agent_factory: AIAgentFactory,
    ):
        with patch("snake.agents.SnakeGameFactory.create_snake_game") as mocked_create_snake_game:
            agent = ai_agent_factory.create_agent()
            agent.restart_game()

            assert mocked_create_snake_game.call_count == 2

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "action, new_direction, expected_snake",
        (
            (Actions.STRAIGHT, Direction.RIGHT, [Point(x=55, y=25), Point(x=50, y=25), Point(x=45, y=25)]),
            (Actions.RIGHT_TURN, Direction.DOWN, [Point(x=50, y=30), Point(x=50, y=25), Point(x=45, y=25)]),
            (Actions.LEFT_TURN, Direction.UP, [Point(x=50, y=20), Point(x=50, y=25), Point(x=45, y=25)]),
        ),
        ids=[
            "Initial direction is 'right' (default), action is 'straight' hence new direction will remain 'right.",
            "Initial direction is 'right' (default), action is 'right_turn' hence new direction will change to 'down'.",
            "Initial direction is 'right' (default), action is 'left_turn' hence new direction will remain 'left'.",
        ],
    )
    def test_play_game_converts_action_correctly_into_directions(
        self,
        _,
        action: Actions,
        new_direction: Direction,
        expected_snake: List[Point],
        ai_agent_factory: AIAgentFactory,
    ):
        with patch("snake.agents.AIAgent._get_actions", return_value=action):
            agent = ai_agent_factory.create_agent()
            assert agent.game.get_current_direction() == Direction.RIGHT
            agent.play_game()
            assert agent.game.get_current_direction() == new_direction
            assert agent.get_snake() == expected_snake

    @pytest.mark.integration
    def test_run_snake_movement_for_multiple_inputs(
        self,
        _,
        ai_agent_factory: AIAgentFactory,
    ):
        actions = [Actions.STRAIGHT, Actions.RIGHT_TURN, Actions.STRAIGHT, Actions.LEFT_TURN, Actions.STRAIGHT]
        agent = ai_agent_factory.create_agent()

        for action in actions:
            with patch("snake.agents.AIAgent._get_actions", return_value=action):
                agent.play_game()

        assert agent.get_snake() == [Point(x=65, y=35), Point(x=60, y=35), Point(x=55, y=35)]
