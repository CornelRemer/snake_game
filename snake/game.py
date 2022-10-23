from tenacity import retry, retry_if_exception_type, stop_after_attempt

from snake.collision_checker import CollisionChecker
from snake.config import GameConfig, WindowConfig
from snake.exceptions import FoodPlacedInSnakeException
from snake.game_controls import Direction, PygameEventHandler
from snake.game_objects.objects import FoodHandler, SnakeHandler
from snake.pygame_interface.game_ui import GameUI


class SnakeGame:
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        window_config: WindowConfig,
        snake_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        self._direction = Direction.RIGHT

        self._snake_handler = snake_handler

        self._score = 0
        self._food_handler = food_handler
        self._food_handler.move_food_to_random_position()
        self._collision_checker = CollisionChecker(
            window_config=window_config, snake_config=snake_config, snake_handler=snake_handler
        )
        self._event_handler = PygameEventHandler()

        self._ui = GameUI(
            window_config=window_config,
            snake_config=snake_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )
        self._game_over = False

    def run(self):
        self._gather_user_input_and_set_new_direction()
        self._move_snake_and_check_for_collision()
        self._handle_snake_reached_food()
        self._update_ui()

    def _gather_user_input_and_set_new_direction(self) -> None:
        self._event_handler.handle_events()
        new_direction = self._event_handler.get_updated_direction()
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
        return self._game_over or self._event_handler.quit_game()

    def get_score(self) -> int:
        return self._score