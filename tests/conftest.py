from typing import Tuple, cast

import pygame
import pytest

from snake.colors import RGBColorCode
from snake.config import GameConfig, WindowConfig
from snake.game_objects.objects import Food, FoodHandler, Point, Snake, SnakeHandler
from tests.fake_classes import FakePublisher, FakeSubscriber


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    # pylint: disable=E1101
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(name="window_config")
def fixture_window_config() -> WindowConfig:
    return WindowConfig(
        height=50,
        width=100,
        background_color=cast(Tuple[int, int, int], RGBColorCode["DARKGREY"].value),
        font_color=cast(Tuple[int, int, int], RGBColorCode["WHITE"].value),
    )


@pytest.fixture(name="game_config")
def fixture_game_config() -> GameConfig:
    return GameConfig(
        frame_rate=2,
        start_length=2,
        outer_block_size=5,
        inner_block_size=3,
        outer_block_color=cast(Tuple[int, int, int], RGBColorCode["DARKGREY"].value),
        inner_block_color=cast(Tuple[int, int, int], RGBColorCode["GREEN"].value),
        food_color=cast(Tuple[int, int, int], RGBColorCode["RED"].value),
        agent_type="USER",
    )


@pytest.fixture(name="food")
def fixture_food(window_config: WindowConfig, game_config: GameConfig) -> Food:
    return Food(width=window_config.width, height=window_config.height, block_size=game_config.outer_block_size)


@pytest.fixture(name="snake")
def fixture_snake() -> Snake:
    return Snake(head=Point(x=50, y=25), body=[Point(x=45, y=25), Point(x=40, y=25)], block_size=5)


@pytest.fixture(name="snake_handler")
def fixture_snake_handler(snake: Snake) -> SnakeHandler:
    return SnakeHandler(snake=snake)


@pytest.fixture(name="food_handler")
def fixture_food_handler(food: Food, window_config: WindowConfig) -> FoodHandler:
    return FoodHandler(food=food, window_config=window_config)


@pytest.fixture(name="fake_publisher")
def fixture_fake_publisher() -> FakePublisher:
    return FakePublisher()


@pytest.fixture(name="fake_subscriber")
def fixture_fake_subscriber() -> FakeSubscriber:
    return FakeSubscriber()
