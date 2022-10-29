from enum import Enum, auto
from typing import List, Optional
from unittest.mock import patch

import pytest

from snake.agents import UserAgent
from snake.config import GameConfig, WindowConfig
from snake.game import SnakeGame
from snake.game_controls import AbstractEventHandler, Direction
from snake.game_objects.objects import FoodHandler, Point, SnakeHandler


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
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
        fake_event_handler: FakeEventHandler,
    ):
        game = SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )

        fake_event = [FakeEvents.QUIT]
        fake_event_handler.add_test_events(fake_event)

        with (
            patch("snake.agents.PygameEventHandler", return_value=fake_event_handler),
            patch("snake.agents.input", return_value=users_input),
        ):
            agent = UserAgent(game=game, window_configuration=window_config, game_configuration=game_config)
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
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        game = SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )

        with (
            patch("snake.agents.SnakeGame.is_over", return_value=game_is_over),
            patch("snake.agents.PygameEventHandler.quit_game", return_value=quit_game),
            patch("snake.agents.input", return_value=users_input),
        ):
            agent = UserAgent(game=game, window_configuration=window_config, game_configuration=game_config)

            assert agent.wants_to_play() == expected_answer

    def test_restart_game(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        game = SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )

        with (
            patch("snake.agents.SnakeGame.is_over", return_value=True),
            patch("snake.agents.input", return_value="n"),
            patch("snake.agents.UserAgent.restart_game") as mocked_restart_game,
        ):
            agent = UserAgent(game=game, window_configuration=window_config, game_configuration=game_config)
            agent.play_game()

            assert not agent.wants_to_play()
            assert mocked_restart_game.call_count == 1

    def test_reset_game(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        game = SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )

        agent = UserAgent(game=game, window_configuration=window_config, game_configuration=game_config)

        assert game == agent.game

        agent.restart_game()

        assert game != agent.game

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
        window_config: WindowConfig,
        game_config: GameConfig,
        fake_event_handler: FakeEventHandler,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
        input_event: List[Optional[FakeEvents]],
        expected_snake: List[Point],
    ):
        fake_event_handler.add_test_events(input_event)

        game = SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )

        with patch("snake.agents.PygameEventHandler", return_value=fake_event_handler):
            agent = UserAgent(game=game, window_configuration=window_config, game_configuration=game_config)
            agent.play_game()

            assert agent.get_snake() == expected_snake

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "initial_direction, updated_direction, expected_snake",
        (
            ([FakeEvents.RIGHT], [FakeEvents.LEFT], [Point(x=60, y=25), Point(x=55, y=25), Point(x=50, y=25)]),
            ([FakeEvents.LEFT], [FakeEvents.RIGHT], [Point(x=60, y=25), Point(x=55, y=25), Point(x=50, y=25)]),
            ([FakeEvents.UP], [FakeEvents.DOWN], [Point(x=50, y=15), Point(x=50, y=20), Point(x=50, y=25)]),
            ([FakeEvents.DOWN], [FakeEvents.UP], [Point(x=50, y=35), Point(x=50, y=30), Point(x=50, y=25)]),
        ),
        ids=[
            "initial direction right, updated direction left -> snake must not change direction.",
            "initial direction left, updated direction right -> snake must not change direction.",
            "initial direction up, updated direction down -> snake must not change direction.",
            "initial direction down, updated direction up -> snake must not change direction.",
        ],
    )
    def test_play_game_with_user_input_does_not_move_snake_to_opposite_direction(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
        fake_event_handler: FakeEventHandler,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
        initial_direction: List[Optional[FakeEvents]],
        updated_direction: List[Optional[FakeEvents]],
        expected_snake: List[Point],
    ):
        fake_event_handler.add_test_events(initial_direction)

        game = SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )

        with patch("snake.agents.PygameEventHandler", return_value=fake_event_handler):
            agent = UserAgent(game=game, window_configuration=window_config, game_configuration=game_config)

            agent.play_game()
            fake_event_handler.add_test_events(updated_direction)
            agent.play_game()

            assert agent.get_snake() == expected_snake

    @pytest.mark.integration
    def test_run_snake_movement_for_multiple_inputs(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
        fake_event_handler: FakeEventHandler,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        fake_events = [None, None, Direction.DOWN, None, Direction.LEFT, FakeEvents.QUIT]

        game = SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )

        with (
            patch("snake.agents.PygameEventHandler", return_value=fake_event_handler),
            patch("snake.agents.input", return_value="n"),
        ):
            agent = UserAgent(game=game, window_configuration=window_config, game_configuration=game_config)

            for fake_event in fake_events:
                fake_event_handler.add_test_events([fake_event])
                agent.play_game()

            assert agent.get_snake() == [Point(x=80, y=25), Point(x=75, y=25), Point(x=70, y=25)]
            assert not agent.wants_to_play()
