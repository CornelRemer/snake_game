from typing import List

import pytest

from snake.config import WindowConfig
from snake.game_controls import Direction
from snake.game_objects.objects import Food, FoodHandler, Point, SnakeHandler


class TestSnakeHandler:
    @pytest.mark.parametrize(
        "direction, expected_snake",
        (
            (Direction.RIGHT, [Point(x=55, y=25), Point(x=50, y=25), Point(x=45, y=25)]),
            (Direction.LEFT, [Point(x=45, y=25), Point(x=50, y=25), Point(x=45, y=25)]),
            (Direction.DOWN, [Point(x=50, y=30), Point(x=50, y=25), Point(x=45, y=25)]),
            (Direction.UP, [Point(x=50, y=20), Point(x=50, y=25), Point(x=45, y=25)]),
        ),
        ids=[
            "move right",
            "move left",
            "move down",
            "move up",
        ],
    )
    def test_move_snake(self, snake_handler: SnakeHandler, direction: Direction, expected_snake: List[Point]):
        snake_handler.move_snake(direction)
        assert snake_handler.get_snake() == expected_snake

    def test_extend_snake(self, snake_handler: SnakeHandler):
        snake_handler.extend_snake(Point(55, 25))
        actual_snake = snake_handler.get_snake()
        expected_snake = [
            Point(55, 25),
            Point(50, 25),
            Point(45, 25),
            Point(40, 25),
        ]
        assert expected_snake == actual_snake

    def test_remove_last_element_from_body(self, snake_handler: SnakeHandler):
        snake_handler.remove_last_element_from_body()
        actual_snake = snake_handler.get_snake()
        expected_snake = [
            Point(50, 25),
            Point(45, 25),
        ]
        assert expected_snake == actual_snake

    def test_snake_bites_itself(self, snake_handler: SnakeHandler):
        snake_handler.extend_snake(Point(45, 25))
        assert snake_handler.snake_bites_itself()

    def test_snake_does_not_bite_itself(self, snake_handler: SnakeHandler):
        assert not snake_handler.snake_bites_itself()

    def test_get_snake(self, snake_handler: SnakeHandler):
        actual_snake = snake_handler.get_snake()
        expected_snake = [
            Point(50, 25),
            Point(45, 25),
            Point(40, 25),
        ]
        assert expected_snake == actual_snake


class TestFoodHandler:
    def test_get_current_food_position(self, food: Food, window_config: WindowConfig):
        food_handler = FoodHandler(food=food, window_config=window_config)
        assert food_handler.get_current_food_position() == Point(window_config.width, window_config.height)

    @pytest.mark.parametrize(
        "test_food",
        [
            Food(width=0, height=0, block_size=5),
            Food(width=100, height=0, block_size=5),
            Food(width=0, height=50, block_size=5),
            Food(width=100, height=50, block_size=5),
        ],
        ids=[
            "Food position: top left hand corner",
            "Food position: top right hand corner",
            "Food position: bottom left hand corner",
            "Food position: bottom right hand corner",
        ],
    )
    def test_move_food_to_random_position_within_window_boundary(self, test_food: Food, window_config: WindowConfig):
        food_handler = FoodHandler(food=test_food, window_config=window_config)
        food_handler.move_food_to_random_position()
        current_position = food_handler.get_current_food_position()
        assert current_position.x >= 0
        assert current_position.x <= window_config.width - test_food.block_size
        assert current_position.y >= 0
        assert current_position.y <= window_config.height - test_food.block_size
