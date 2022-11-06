from snake.config import GameConfig, WindowConfig
from snake.game_objects.objects import Point, SnakeHandler


class CollisionChecker:
    def __init__(self, window_config: WindowConfig, game_config: GameConfig, snake_handler: SnakeHandler):
        self._window_config = window_config
        self._game_config = game_config
        self._snake_handler = snake_handler

    def collision_detected(self) -> bool:
        snake_head = self._snake_handler.head
        return self._snake_bites_itself() or self._collision_between_point_and_window_boundary(point=snake_head)

    def _snake_bites_itself(self) -> bool:
        return self._snake_handler.snake_bites_itself()

    def _collision_between_point_and_window_boundary(self, point: Point) -> bool:
        return (
            self.point_top_collision(point=point)
            or self.point_bottem_collision(point=point)
            or self.point_left_boundary_collision(point=point)
            or self.point_right_boundary_collision(point=point)
        )

    @staticmethod
    def point_top_collision(point: Point) -> bool:
        return point.y < 0

    def point_bottem_collision(self, point: Point) -> bool:
        return point.y > self._window_config.height - self._game_config.outer_block_size

    @staticmethod
    def point_left_boundary_collision(point: Point) -> bool:
        return point.x < 0

    def point_right_boundary_collision(self, point: Point) -> bool:
        return point.x > self._window_config.width - self._game_config.outer_block_size
