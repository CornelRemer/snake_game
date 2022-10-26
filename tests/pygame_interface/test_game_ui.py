from unittest.mock import patch

from snake.config import GameConfig, WindowConfig
from snake.game_objects.objects import FoodHandler, SnakeHandler
from snake.pygame_interface.game_ui import GameUI


@patch("snake.pygame_interface.game_ui.pygame.display")
class TestPyGameUI:
    def test_update_clock(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        game_config.frame_rate = 30
        pygame_ui = GameUI(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )
        # pylint: disable=W0212
        old_time = pygame_ui._clock.get_time()
        pygame_ui.update_clock()
        actual_time_delta = pygame_ui._clock.get_time() - old_time
        expected_time_delta = 1_000 / game_config.frame_rate
        assert actual_time_delta >= int(expected_time_delta * 0.95)

    def test_update_snake_food_and_text(
        self,
        _,
        window_config: WindowConfig,
        game_config: GameConfig,
        snake_handler: SnakeHandler,
        food_handler: FoodHandler,
    ):
        pygame_ui = GameUI(
            window_config=window_config,
            game_config=game_config,
            snake_handler=snake_handler,
            food_handler=food_handler,
        )
        test_score = 100
        with patch("snake.pygame_interface.game_ui.pygame.draw.rect") as mocked_draw_rect:
            pygame_ui.update_snake_food_and_text(score=test_score)

            head_size = 1
            outer_block_count = head_size + game_config.start_length
            inner_block_count = head_size + game_config.start_length
            food_count = 1
            expected_number_of_rectangles = outer_block_count + inner_block_count + food_count

            actual_number_of_rectangles = mocked_draw_rect.call_count
            assert actual_number_of_rectangles == expected_number_of_rectangles
