import pytest

from snake.collision_checker import CollisionChecker
from snake.config import GameConfig, WindowConfig
from snake.game_objects.objects import Point, Snake, SnakeHandler


class TestCollisionChecker:
    @pytest.mark.parametrize(
        "test_snake, expected_collision",
        [
            (Snake(head=Point(x=50, y=-1), body=[Point(0, 0), Point(0, 0)], block_size=5), True),
            (Snake(head=Point(x=50, y=46), body=[Point(0, 0), Point(0, 0)], block_size=5), True),
            (Snake(head=Point(x=-1, y=25), body=[Point(0, 0), Point(0, 0)], block_size=5), True),
            (Snake(head=Point(x=96, y=25), body=[Point(0, 0), Point(0, 0)], block_size=5), True),
        ],
        ids=[
            "snake hit top",
            "snake hit bottom",
            "snake hit left side",
            "snake hit right side",
        ],
    )
    def test_collision_detected_with_window_boundaries(
        self, test_snake: Snake, expected_collision: bool, window_config: WindowConfig, snake_config: GameConfig
    ):
        snake_handler = SnakeHandler(snake=test_snake)
        collision_checker = CollisionChecker(
            window_config=window_config, snake_config=snake_config, snake_handler=snake_handler
        )
        assert collision_checker.collision_detected() == expected_collision

    @pytest.mark.parametrize(
        "test_snake, expected_collision",
        [
            (Snake(head=Point(x=50, y=0), body=[Point(0, 0), Point(0, 0)], block_size=5), False),
            (Snake(head=Point(x=50, y=45), body=[Point(0, 0), Point(0, 0)], block_size=5), False),
            (Snake(head=Point(x=0, y=25), body=[Point(0, 0), Point(0, 0)], block_size=5), False),
            (Snake(head=Point(x=95, y=25), body=[Point(0, 0), Point(0, 0)], block_size=5), False),
            (Snake(head=Point(x=50, y=25), body=[Point(0, 0), Point(0, 0)], block_size=5), False),
        ],
        ids=[
            "snake does not hit top",
            "snake does not hit bottom",
            "snake does not hit left side",
            "snake does not hit right side",
            "snake is in window center",
        ],
    )
    def test_collision_detected_with_no_collision(
        self, test_snake: Snake, expected_collision: bool, window_config: WindowConfig, snake_config: GameConfig
    ):
        snake_handler = SnakeHandler(snake=test_snake)
        collision_checker = CollisionChecker(
            window_config=window_config, snake_config=snake_config, snake_handler=snake_handler
        )
        assert collision_checker.collision_detected() == expected_collision
