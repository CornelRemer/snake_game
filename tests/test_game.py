from typing import List
from unittest.mock import patch

import pytest

from snake.config import GameConfig, WindowConfig
from snake.game import SnakeGame
from snake.game_controls import Direction
from snake.game_objects.objects import Food, FoodHandler, Point, Snake, SnakeHandler


@pytest.fixture(name="snake_game")
def fixture_test_game(
    window_config: WindowConfig,
    game_config: GameConfig,
    snake_handler: SnakeHandler,
    food_handler: FoodHandler,
) -> SnakeGame:
    with patch("snake.game.GameUI"):
        return SnakeGame(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )


@patch("snake.game.GameUI")
class TestSnakeGame:
    # pylint: disable=too-many-arguments

    @pytest.mark.parametrize(
        "input_direction, expected_snake",
        (
            (None, [Point(x=55, y=25), Point(x=50, y=25), Point(x=45, y=25)]),
            (Direction.RIGHT, [Point(x=55, y=25), Point(x=50, y=25), Point(x=45, y=25)]),
            (Direction.UP, [Point(x=50, y=20), Point(x=50, y=25), Point(x=45, y=25)]),
            (Direction.DOWN, [Point(x=50, y=30), Point(x=50, y=25), Point(x=45, y=25)]),
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
        snake_game: SnakeGame,
        snake_handler: SnakeHandler,
        input_direction: Direction,
        expected_snake: List[Point],
    ):
        snake_game.update_direction(input_direction)
        snake_game.run()
        assert snake_handler.get_snake() == expected_snake

    @pytest.mark.parametrize(
        "initial_direction, updated_direction, expected_snake",
        (
            (Direction.RIGHT, Direction.LEFT, [Point(x=60, y=25), Point(x=55, y=25), Point(x=50, y=25)]),
            (Direction.LEFT, Direction.RIGHT, [Point(x=60, y=25), Point(x=55, y=25), Point(x=50, y=25)]),
            (Direction.UP, Direction.DOWN, [Point(x=50, y=15), Point(x=50, y=20), Point(x=50, y=25)]),
            (Direction.DOWN, Direction.UP, [Point(x=50, y=35), Point(x=50, y=30), Point(x=50, y=25)]),
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
        snake_game: SnakeGame,
        snake_handler: SnakeHandler,
        initial_direction: Direction,
        updated_direction: Direction,
        expected_snake: List[Point],
    ):
        snake_game.update_direction(initial_direction)
        snake_game.run()
        snake_game.update_direction(updated_direction)
        snake_game.run()

        assert snake_handler.get_snake() == expected_snake

    def test_run_snake_movement_for_multiple_inputs(
        self,
        _,
        snake_game: SnakeGame,
        snake_handler: SnakeHandler,
    ):
        input_directions = [None, None, Direction.DOWN, None, Direction.UP]

        for direction in input_directions:
            snake_game.update_direction(direction)
            snake_game.run()

        assert snake_handler.get_snake() == [Point(x=60, y=40), Point(x=60, y=35), Point(x=60, y=30)]

    def test_run_quits_game_on_collision(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        with patch("snake.game.CollisionChecker.collision_detected", return_value=True):
            game = SnakeGame(
                window_config=window_config,
                game_config=game_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            game.run()

            assert game.is_over()

    def test_run_increases_score_when_snake_reaches_food(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
    ):
        snake = Snake(head=Point(x=50, y=25), body=[Point(x=45, y=25), Point(x=40, y=25)], block_size=5)
        snake_handler = SnakeHandler(snake=snake)

        food = Food(width=55, height=25, block_size=game_config.outer_block_size)
        food_handler = FoodHandler(food=food, window_config=window_config)

        with patch("snake.game.FoodHandler.move_food_to_random_position"), patch(
            "snake.game.SnakeGame._place_new_food"
        ):
            game = SnakeGame(
                window_config=window_config,
                game_config=game_config,
                snake_handler=snake_handler,
                food_handler=food_handler,
            )
            assert game.get_score() == 0

            game.run()

            assert game.get_score() == 1
