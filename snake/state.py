from typing import List

import numpy as np

from snake.collision_checker import CollisionChecker
from snake.config import GameConfig
from snake.game import SnakeGame
from snake.game_controls import Direction
from snake.game_objects.objects import Point


class State:
    def __init__(self, game: SnakeGame, game_config: GameConfig):
        self._game = game
        self._block_size = game_config.outer_block_size

    @property
    def _collision_checker(self) -> CollisionChecker:
        return self._game.get_collision_checker()

    def calculate_state_from_game(
        self,
    ):
        hazards = self.calculate_location_of_hazard_as_binary()
        direction = self.convert_direction_to_binary()
        food_position = self.calculate_current_food_position_relative_to_snake_as_binary()

        return np.array(hazards + direction + food_position, dtype=int)

    # ToDo: refactor
    def calculate_location_of_hazard_as_binary(self) -> List[int]:
        snake_head = self._game.get_snake()[0]
        direction = self._game.get_current_direction()

        point_above = Point(x=snake_head.x, y=snake_head.y - self._block_size)
        point_below = Point(x=snake_head.x, y=snake_head.y + self._block_size)
        point_left_side = Point(x=snake_head.x - self._block_size, y=snake_head.y)
        point_right_side = Point(x=snake_head.x + self._block_size, y=snake_head.y)

        hazard_straight = (
            (direction is Direction.RIGHT and self._collision_checker.point_right_boundary_collision(point_right_side))
            or (direction is Direction.LEFT and self._collision_checker.point_left_boundary_collision(point_left_side))
            or (direction is Direction.UP and self._collision_checker.point_top_collision(point_above))
            or (direction is Direction.DOWN and self._collision_checker.point_bottem_collision(point_below))
        )

        hazard_right = (
            (direction is Direction.RIGHT and self._collision_checker.point_bottem_collision(point_below))
            or (direction is Direction.LEFT and self._collision_checker.point_top_collision(point_above))
            or (direction is Direction.UP and self._collision_checker.point_right_boundary_collision(point_right_side))
            or (direction is Direction.DOWN and self._collision_checker.point_left_boundary_collision(point_left_side))
        )

        hazard_left = (
            (direction is Direction.RIGHT and self._collision_checker.point_top_collision(point_above))
            or (direction is Direction.LEFT and self._collision_checker.point_bottem_collision(point_below))
            or (direction is Direction.UP and self._collision_checker.point_left_boundary_collision(point_left_side))
            or (
                direction is Direction.DOWN and self._collision_checker.point_right_boundary_collision(point_right_side)
            )
        )

        return [hazard_straight, hazard_right, hazard_left]

    def convert_direction_to_binary(self) -> List[int]:
        current_direction = self._game.get_current_direction()
        return [int(current_direction is direction) for direction in Direction]

    def calculate_current_food_position_relative_to_snake_as_binary(self):
        snake_head = self._game.get_snake()[0]
        food_position = self._game.get_food()
        return [
            food_position.x < snake_head.x,  # Food is to the left of the snakes head
            food_position.x > snake_head.x,  # Food is to the right of the snakes head
            food_position.y < snake_head.y,  # Food is above the snakes head
            food_position.y > snake_head.y,  # Food is below the snakes head
        ]


class StateFactory:
    def __init__(self, game_configuration: GameConfig):
        self._game_config = game_configuration

    def create_state_for_game(self, game: SnakeGame) -> State:
        return State(game=game, game_config=self._game_config)
