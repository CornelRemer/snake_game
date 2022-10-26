from snake.config import GameConfig, WindowConfig
from snake.game_objects.objects import SnakeHandler


class CollisionChecker:
    def __init__(self, window_config: WindowConfig, game_config: GameConfig, snake_handler: SnakeHandler):
        self._window_config = window_config
        self._game_config = game_config
        self._snake_handler = snake_handler

    def collision_detected(self) -> bool:
        return self._snake_bites_itself() or self._snake_hits_window_boundary()

    def _snake_bites_itself(self) -> bool:
        return self._snake_handler.snake_bites_itself()

    def _snake_hits_window_boundary(self) -> bool:
        return (
            self._snake_hit_top()
            or self._snake_hit_bottem()
            or self._snake_hit_left_side()
            or self._snake_hit_right_side()
        )

    def _snake_hit_top(self) -> bool:
        snake_head = self._snake_handler.head
        return snake_head.y < 0

    def _snake_hit_bottem(self) -> bool:
        snake_head = self._snake_handler.head
        return snake_head.y > self._window_config.height - self._game_config.outer_block_size

    def _snake_hit_left_side(self) -> bool:
        snake_head = self._snake_handler.head
        return snake_head.x < 0

    def _snake_hit_right_side(self) -> bool:
        snake_head = self._snake_handler.head
        return snake_head.x > self._window_config.width - self._game_config.outer_block_size
