from typing import Tuple

import pygame

from snake.config import GameConfig, WindowConfig
from snake.fonts import Arial
from snake.game_objects.objects import FoodHandler, Point, SnakeHandler


class GameUI:
    def __init__(
        self,
        window_config: WindowConfig,
        snake_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        self._window_config = window_config
        self._snake_config = snake_config
        self._display = pygame.display.set_mode((window_config.width, window_config.height))
        self._clock = pygame.time.Clock()
        self._snake_handler = snake_handler
        self._food_handler = food_handler

        pygame.display.set_caption(self.__class__.__name__)

    def update_snake_food_and_text(self, score: int):
        self._set_background_color()
        self._draw_snake()
        self._draw_food()
        self._draw_score_text(score)
        pygame.display.flip()

    def _set_background_color(self) -> None:
        self._display.fill(self._window_config.background_color)

    def _draw_snake(self) -> None:
        block_margin = self._calculate_block_margin()
        for element in self._snake_handler.get_snake():
            self._draw_square(
                x=element.x,
                y=element.y,
                color=self._snake_config.outer_block_color,
                size=self._snake_config.outer_block_size,
            )
            self._draw_square(
                x=element.x + block_margin,
                y=element.y + block_margin,
                color=self._snake_config.inner_block_color,
                size=self._snake_config.inner_block_size,
            )

    def _calculate_block_margin(self) -> int:
        return abs(self._snake_config.outer_block_size - self._snake_config.inner_block_size) // 2

    def _draw_square(self, x: int, y: int, color: Tuple[int, int, int], size: int) -> None:
        pygame.draw.rect(surface=self._display, color=color, rect=pygame.Rect(x, y, size, size))

    def _draw_food(self) -> None:
        food_position = self._calculate_food_position_with_margin()
        self._draw_square(
            *food_position,
            color=self._snake_config.food_color,
            size=self._snake_config.inner_block_size,
        )

    def _calculate_food_position_with_margin(self) -> Point:
        block_margin = self._calculate_block_margin()
        food_position = self._food_handler.get_current_food_position()
        return Point(x=food_position.x + block_margin, y=food_position.y + block_margin)

    def _draw_score_text(self, score: int):
        font = Arial(font_size=25).font
        text = font.render(f"Score {score}", True, self._window_config.font_color)
        self._display.blit(text, [0, 0])

    def update_clock(self) -> None:
        self._clock.tick(self._snake_config.frame_rate)
