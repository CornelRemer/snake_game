from typing import List
from unittest.mock import Mock, patch

import numpy as np
import pytest

from snake.config import GameConfig
from snake.game import SnakeGame
from snake.game_controls import Direction
from snake.game_objects.objects import Point
from snake.state import State


class TestState:
    # pylint: disable=too-many-arguments
    @pytest.mark.parametrize(
        "current_direction, snake_head, expected_location_of_hazard",
        (
            (Direction.RIGHT, Point(x=95, y=25), [1, 0, 0]),
            (Direction.UP, Point(x=50, y=0), [1, 0, 0]),
            (Direction.LEFT, Point(x=0, y=25), [1, 0, 0]),
            (Direction.DOWN, Point(x=50, y=45), [1, 0, 0]),
            (Direction.RIGHT, Point(x=50, y=45), [0, 1, 0]),
            (Direction.UP, Point(x=95, y=25), [0, 1, 0]),
            (Direction.LEFT, Point(x=50, y=0), [0, 1, 0]),
            (Direction.DOWN, Point(x=0, y=25), [0, 1, 0]),
            (Direction.RIGHT, Point(x=50, y=0), [0, 0, 1]),
            (Direction.UP, Point(x=0, y=25), [0, 0, 1]),
            (Direction.LEFT, Point(x=50, y=45), [0, 0, 1]),
            (Direction.DOWN, Point(x=95, y=25), [0, 0, 1]),
            (Direction.UP, Point(x=95, y=0), [1, 1, 0]),
            (Direction.RIGHT, Point(x=95, y=0), [1, 0, 1]),
            (Direction.LEFT, Point(x=0, y=0), [1, 1, 0]),
            (Direction.UP, Point(x=0, y=0), [1, 0, 1]),
            (Direction.DOWN, Point(x=0, y=45), [1, 1, 0]),
            (Direction.LEFT, Point(x=0, y=45), [1, 0, 1]),
            (Direction.RIGHT, Point(x=95, y=45), [1, 1, 0]),
            (Direction.DOWN, Point(x=95, y=45), [1, 0, 1]),
        ),
        ids=[
            "Snake moves right and is about to hit the right boundary -> straight hazard",
            "Snake moves up and is about to hit the top boundary -> straight hazard",
            "Snake moves left and is about to hit the left boundary -> straight hazard",
            "Snake moves down and is about to hit the bottom boundary -> straight hazard",
            "Snake moves right along the bottom boundary -> right hazard",
            "Snake moves up along the right boundary -> right hazard",
            "Snake moves left along the top boundary -> right hazard",
            "Snake moves down along the left boundary -> right hazard",
            "Snake moves right along the top boundary -> left hazard",
            "Snake moves up along the left boundary -> left hazard",
            "Snake moves left along the bottom boundary -> left hazard",
            "Snake moves down along the right boundary -> left hazard",
            "Snake moves up, head is located in top right hand corner -> right and straight hazard",
            "Snake moves right, head is located in top right hand corner -> left and straight hazard",
            "Snake moves left, head is located in top left hand corner -> right and straight hazard",
            "Snake moves up, head is located in top left hand corner -> left and straight hazard",
            "Snake moves down, head is located in bottom left hand corner -> right and straight hazard",
            "Snake moves left, head is located in bottom left hand corner -> left and straight hazard",
            "Snake moves right, head is located in bottom right hand corner -> right and straight hazard",
            "Snake moves down, head is located in bottom right hand corner -> left and straight hazard",
        ],
    )
    def test_calculate_location_of_hazard_as_binary(
        self,
        current_direction: Direction,
        snake_head: Point,
        expected_location_of_hazard: List[int],
        snake_game: SnakeGame,
        game_config: GameConfig,
    ):
        with (
            patch("snake.game.SnakeGame.get_current_direction", return_value=current_direction),
            patch("snake.game.SnakeGame.get_snake", return_value=[snake_head]),
        ):
            state = State(game=snake_game, game_config=game_config)
            actual_location_of_hazard = state.calculate_location_of_hazard_as_binary()

        assert actual_location_of_hazard == expected_location_of_hazard
        assert len(actual_location_of_hazard) == 3

    @pytest.mark.parametrize(
        "current_direction, expected_binary_expression",
        (
            (Direction.RIGHT, [1, 0, 0, 0]),
            (Direction.LEFT, [0, 1, 0, 0]),
            (Direction.UP, [0, 0, 1, 0]),
            (Direction.DOWN, [0, 0, 0, 1]),
        ),
    )
    def test_convert_direction_to_binary(
        self,
        current_direction: Direction,
        expected_binary_expression: List[int],
        snake_game: SnakeGame,
        game_config: GameConfig,
    ):
        with patch("snake.state.SnakeGame.get_current_direction", return_value=current_direction):
            state = State(game=snake_game, game_config=game_config)
            actual_binary_expression = state.convert_direction_to_binary()

        assert actual_binary_expression == expected_binary_expression
        assert len(actual_binary_expression) == 4

    @pytest.mark.parametrize(
        "snake_head, food_position, expected_binary_position",
        (
            (Point(x=10, y=0), Point(x=5, y=0), [1, 0, 0, 0]),
            (Point(x=5, y=0), Point(x=10, y=0), [0, 1, 0, 0]),
            (Point(x=0, y=10), Point(x=0, y=5), [0, 0, 1, 0]),
            (Point(x=0, y=5), Point(x=0, y=10), [0, 0, 0, 1]),
            (Point(x=10, y=10), Point(x=5, y=5), [1, 0, 1, 0]),
            (Point(x=10, y=5), Point(x=5, y=10), [1, 0, 0, 1]),
            (Point(x=5, y=10), Point(x=10, y=5), [0, 1, 1, 0]),
            (Point(x=5, y=5), Point(x=10, y=10), [0, 1, 0, 1]),
        ),
        ids=[
            "Food is to the left of the snakes head.",
            "Food is to the right of the snakes head.",
            "Food is above the snakes head.",
            "Food is below the snakes head.",
            "Food is to the left and above the snakes head.",
            "Food is to the left and below the snakes head.",
            "Food is to the right and above the snakes head.",
            "Food is to the right and below the snakes head.",
        ],
    )
    def test_calculate_current_food_position_relative_to_snake_as_binary(
        self,
        snake_head: Point,
        food_position: Point,
        expected_binary_position: List[int],
        snake_game: SnakeGame,
        game_config: GameConfig,
    ):
        with (
            patch("snake.game.SnakeGame.get_snake", return_value=[snake_head]),
            patch("snake.game.SnakeGame.get_food", return_value=food_position),
        ):
            state = State(game=snake_game, game_config=game_config)
            actual_binary_position = state.calculate_current_food_position_relative_to_snake_as_binary()
        assert actual_binary_position == expected_binary_position
        assert len(actual_binary_position) == 4

    def test_calculate_state_from_game(self, snake_game: SnakeGame, game_config: GameConfig):
        hazards = [1, 0, 1]
        direction = [1, 0, 0, 0]
        food_position = [1, 0, 0, 0]
        expected_state = hazards + direction + food_position

        with patch.multiple(
            "snake.state.State",
            calculate_location_of_hazard_as_binary=Mock(return_value=hazards),
            convert_direction_to_binary=Mock(return_value=direction),
            calculate_current_food_position_relative_to_snake_as_binary=Mock(return_value=food_position),
        ):
            state = State(game=snake_game, game_config=game_config)
            actual_state = state.calculate_state_from_game()

        assert np.array_equal(actual_state, expected_state)
        assert len(actual_state) == 11
