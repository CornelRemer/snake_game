from snake.config import GameConfig, WindowConfig
from snake.game_objects.objects import Food, FoodHandler, Point, Snake, SnakeHandler


class SnakeFactory:
    def __init__(self, window_config: WindowConfig, snake_config: GameConfig):
        self._window_config = window_config
        self._snake_config = snake_config

    def create_snake(self) -> Snake:
        return Snake(
            head=self._get_window_center(),
            body=[
                Point(
                    self._get_window_center().x - (i + 1) * self._snake_config.outer_block_size,
                    self._get_window_center().y,
                )
                for i in range(self._snake_config.start_length)
            ],
            block_size=self._snake_config.outer_block_size,
        )

    def _get_window_center(self) -> Point:
        return Point(int(self._window_config.width / 2), int(self._window_config.height / 2))


class SnakeHandlerFactory:
    def __init__(self, snake: Snake):
        self._snake = snake

    def create_snake_handler(self) -> SnakeHandler:
        return SnakeHandler(
            snake=self._snake,
        )


class FoodFactory:
    def __init__(self, window_config: WindowConfig, snake_config: GameConfig):
        self._window_config = window_config
        self._snake_config = snake_config

    def create_food(self) -> Food:
        return Food(
            width=self._window_config.width,
            height=self._window_config.height,
            block_size=self._snake_config.outer_block_size,
        )


class FoodHandlerFactory:
    def __init__(self, food: Food, window_config: WindowConfig):
        self._food = food
        self._window_config = window_config

    def create_food_handler(self) -> FoodHandler:
        return FoodHandler(food=self._food, window_config=self._window_config)
