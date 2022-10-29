from typing import List, Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt

from snake.collision_checker import CollisionChecker
from snake.config import GameConfig, WindowConfig
from snake.exceptions import FoodPlacedInSnakeException
from snake.game_controls import Direction
from snake.game_objects.factories import (
    FoodFactory,
    FoodHandlerFactory,
    SnakeFactory,
    SnakeHandlerFactory,
)
from snake.game_objects.objects import FoodHandler, Point, SnakeHandler
from snake.pygame_interface.game_ui import GameUI


class SnakeGame:
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        self._snake_handler = snake_handler
        self._direction = Direction.RIGHT
        self._score = 0
        self._food_handler = food_handler
        self._food_handler.move_food_to_random_position()
        self._collision_checker = CollisionChecker(
            window_config=window_config, game_config=game_config, snake_handler=snake_handler
        )

        self._ui = GameUI(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )
        self._game_over = False

    def run(self):
        self._move_snake_and_check_for_collision()
        self._handle_snake_reached_food()
        self._update_ui()

    def update_direction(self, new_direction: Optional[Direction]):
        if new_direction and self._is_no_opposite_direction(new_direction):
            self._direction = new_direction

    def _is_no_opposite_direction(self, direction: Direction) -> bool:
        invalid_directions = [{Direction.RIGHT, Direction.LEFT}, {Direction.UP, Direction.DOWN}]
        if {self._direction, direction} in invalid_directions:
            return False
        return True

    def _move_snake_and_check_for_collision(self) -> None:
        self._snake_handler.move_snake(self._direction)
        if self._collision_checker.collision_detected():
            self._game_over = True

    def _handle_snake_reached_food(self) -> None:
        if self._snake_reached_food():
            self._score += 1
            self._extend_snake_and_place_new_food()

    def _snake_reached_food(self) -> bool:
        return self._snake_handler.head == self._food_handler.get_current_food_position()

    def _extend_snake_and_place_new_food(self) -> None:
        self._snake_handler.extend_snake(self._food_handler.get_current_food_position())
        self._place_new_food()

    @retry(retry=retry_if_exception_type(FoodPlacedInSnakeException), stop=stop_after_attempt(100))
    def _place_new_food(self) -> None:
        self._food_handler.move_food_to_random_position()

        if self._food_is_located_in_snake():
            raise FoodPlacedInSnakeException(
                f"New random position for food is inside the snake.\n"
                f"food:{self._food_handler.get_current_food_position()}\n"
                f"snake: {self._snake_handler.get_snake()}"
            )

    def _food_is_located_in_snake(self) -> bool:
        return self._food_handler.get_current_food_position() in self._snake_handler.get_snake()

    def _update_ui(self) -> None:
        self._ui.update_snake_food_and_text(score=self._score)
        self._ui.update_clock()

    def is_not_over(self):
        return not self.is_over()

    def is_over(self) -> bool:
        return self._game_over

    def get_score(self) -> int:
        return self._score

    def get_snake(self) -> List[Point]:
        return self._snake_handler.get_snake()


class SnakeGameFactory:
    def __init__(self, window_configuration: WindowConfig, game_configuration: GameConfig):
        self._window_config = window_configuration
        self._game_config = game_configuration

    def create_snake_game(self) -> SnakeGame:
        return SnakeGame(
            window_config=self._window_config,
            game_config=self._game_config,
            snake_handler=SnakeHandlerFactory(
                snake=SnakeFactory(
                    window_config=self._window_config,
                    game_config=self._game_config,
                ).create_snake()
            ).create_snake_handler(),
            food_handler=FoodHandlerFactory(
                food=FoodFactory(window_config=self._window_config, game_config=self._game_config).create_food(),
                window_config=self._window_config,
            ).create_food_handler(),
        )
