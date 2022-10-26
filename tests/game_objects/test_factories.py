from snake.config import GameConfig, WindowConfig
from snake.game_objects.factories import (
    FoodFactory,
    FoodHandlerFactory,
    SnakeFactory,
    SnakeHandlerFactory,
)
from snake.game_objects.objects import Food, FoodHandler, Point, Snake, SnakeHandler


class TestSnakeFactory:
    def test_create_snake_returns_correct_type(self, window_config: WindowConfig, game_config: GameConfig):
        actual_snake = SnakeFactory(window_config=window_config, game_config=game_config).create_snake()
        assert isinstance(actual_snake, Snake)

    def test_create_snake_returns_correct_snake(self, window_config: WindowConfig, game_config: GameConfig):
        actual_snake = SnakeFactory(window_config=window_config, game_config=game_config).create_snake()
        expected_snake = Snake(head=Point(x=50, y=25), body=[Point(x=45, y=25), Point(x=40, y=25)], block_size=5)
        assert actual_snake == expected_snake


class TestSnakeHandlerFactory:
    def test_create_snake_handler_returns_correct_type(self, snake: Snake):
        snake_handler = SnakeHandlerFactory(snake=snake).create_snake_handler()
        assert isinstance(snake_handler, SnakeHandler)

    def test_snake_handler_has_correct_snake(self, snake: Snake):
        snake_handler = SnakeHandlerFactory(snake=snake).create_snake_handler()
        assert snake_handler.get_snake() == snake.elements


class TestFoodFactory:
    def test_create_food_returns_correct_type(self, window_config: WindowConfig, game_config: GameConfig):
        actual_food = FoodFactory(window_config=window_config, game_config=game_config).create_food()
        assert isinstance(actual_food, Food)

    def test_create_food_returns_correct_food(self, window_config: WindowConfig, game_config: GameConfig, food: Food):
        actual_food = FoodFactory(window_config=window_config, game_config=game_config).create_food()
        assert actual_food == food


class TestFoodHandlerFactory:
    def test_create_food_handler_returns_correct_type(self, food: Food, window_config: WindowConfig):
        actual_food_handler = FoodHandlerFactory(food=food, window_config=window_config).create_food_handler()
        assert isinstance(actual_food_handler, FoodHandler)
