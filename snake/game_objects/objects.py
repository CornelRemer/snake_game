import random
from dataclasses import dataclass
from typing import Callable, Dict, List, NamedTuple

from snake.config import WindowConfig
from snake.game_controls import Direction


class Point(NamedTuple):
    x: int
    y: int


@dataclass
class Snake:
    head: Point
    body: List[Point]
    block_size: int

    @property
    def elements(self) -> List[Point]:
        return [self.head] + self.body


class SnakeHandler:
    def __init__(self, snake: Snake):
        self._snake = snake

    def move_snake(self, direction: Direction):
        new_head = self._calculate_new_head(direction)
        self.extend_snake(new_head)
        self.remove_last_element_from_body()

    def _calculate_new_head(self, direction: Direction) -> Point:
        return self._directions[direction](self.head)

    @property
    def _directions(self) -> Dict[Direction, Callable[[Point], Point]]:
        return {
            Direction.RIGHT: lambda point: Point(point.x + self._snake.block_size, point.y),
            Direction.LEFT: lambda point: Point(point.x - self._snake.block_size, point.y),
            Direction.DOWN: lambda point: Point(point.x, point.y + self._snake.block_size),
            Direction.UP: lambda point: Point(point.x, point.y - self._snake.block_size),
        }

    @property
    def head(self) -> Point:
        return self._snake.head

    def extend_snake(self, new_head: Point) -> None:
        self._snake.body.insert(0, self._snake.head)
        self._snake.head = new_head

    def remove_last_element_from_body(self) -> None:
        self._snake.body.pop()

    def snake_bites_itself(self) -> bool:
        return self._snake.head in self._snake.body

    def get_snake(self) -> List[Point]:
        return self._snake.elements


@dataclass
class Food:
    width: int
    height: int
    block_size: int


class FoodHandler:
    def __init__(self, food: Food, window_config: WindowConfig):
        self._food = food
        self._window_config = window_config

    def move_food_to_random_position(self) -> None:
        self._food.width = (
            random.randint(0, self._window_config.width - 1) // self._food.block_size
        ) * self._food.block_size
        self._food.height = (
            random.randint(0, self._window_config.height - 1) // self._food.block_size
        ) * self._food.block_size

    def get_current_food_position(self) -> Point:
        return Point(x=self._food.width, y=self._food.height)
