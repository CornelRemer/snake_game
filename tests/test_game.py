from enum import Enum, auto
from typing import List, Optional
from unittest.mock import patch

import pytest

from snake.config import GameConfig, WindowConfig
from snake.game import SnakeGame
from snake.game_controls import AbstractEventHandler, Direction
from snake.game_objects.objects import Food, FoodHandler, Point, Snake, SnakeHandler


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
class TestSnakeGame:
    # pylint: disable=too-many-arguments
    def test_run_exit_on_quit_event(
        self,
        _,
        window_config: WindowConfig,
        snake_config: GameConfig,
        fake_event_handler: FakeEventHandler,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        fake_event = [FakeEvents.QUIT]
        fake_event_handler.add_test_events(fake_event)

        with patch("snake.game.PygameEventHandler", return_value=fake_event_handler):
            game = SnakeGame(
                window_config=window_config,
                snake_config=snake_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            assert game.is_not_over()

            game.run()

            assert game.is_over()

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
    def test_run_snake_movement_for_different_inputs(
        self,
        _,
        window_config: WindowConfig,
        snake_config: GameConfig,
        fake_event_handler: FakeEventHandler,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
        input_event: List[Optional[FakeEvents]],
        expected_snake: List[Point],
    ):
        fake_event_handler.add_test_events(input_event)

        with patch("snake.game.PygameEventHandler", return_value=fake_event_handler):
            game = SnakeGame(
                window_config=window_config,
                snake_config=snake_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            game.run()
            assert snake_handler.get_snake() == expected_snake

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
    def test_run_snake_does_not_move_to_opposite_direction(
        self,
        _,
        window_config: WindowConfig,
        snake_config: GameConfig,
        fake_event_handler: FakeEventHandler,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
        initial_direction: List[Optional[FakeEvents]],
        updated_direction: List[Optional[FakeEvents]],
        expected_snake: List[Point],
    ):
        fake_event_handler.add_test_events(initial_direction)

        with patch("snake.game.PygameEventHandler", return_value=fake_event_handler):
            game = SnakeGame(
                window_config=window_config,
                snake_config=snake_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            game.run()
            fake_event_handler.add_test_events(updated_direction)
            game.run()

            assert snake_handler.get_snake() == expected_snake

    def test_run_snake_movement_for_multiple_inputs(
        self,
        _,
        window_config: WindowConfig,
        snake_config: GameConfig,
        fake_event_handler: FakeEventHandler,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        fake_events = [None, None, Direction.DOWN, None, Direction.LEFT, FakeEvents.QUIT]
        with patch("snake.game.PygameEventHandler", return_value=fake_event_handler):
            game = SnakeGame(
                window_config=window_config,
                snake_config=snake_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            for fake_event in fake_events:
                fake_event_handler.add_test_events([fake_event])
                game.run()

            assert snake_handler.get_snake() == [Point(x=80, y=25), Point(x=75, y=25), Point(x=70, y=25)]
            assert game.is_over()

    def test_run_quits_game_on_collision(
        self,
        _,
        window_config: WindowConfig,
        snake_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        with patch("snake.game.CollisionChecker.collision_detected", return_value=True):
            game = SnakeGame(
                window_config=window_config,
                snake_config=snake_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            game.run()

            assert game.is_over()

    def test_run_increases_score_when_snake_reaches_food(
        self,
        _,
        window_config: WindowConfig,
        snake_config: GameConfig,
    ):
        snake = Snake(head=Point(x=50, y=25), body=[Point(x=45, y=25), Point(x=40, y=25)], block_size=5)
        snake_handler = SnakeHandler(snake=snake)

        food = Food(width=55, height=25, block_size=snake_config.outer_block_size)
        food_handler = FoodHandler(food=food, window_config=window_config)

        with patch("snake.game.FoodHandler.move_food_to_random_position"), patch(
            "snake.game.SnakeGame._place_new_food"
        ):
            game = SnakeGame(
                window_config=window_config,
                snake_config=snake_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            assert game.get_score() == 0

            game.run()

            assert game.get_score() == 1
