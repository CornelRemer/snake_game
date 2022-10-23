from snake.config import GameConfig, WindowConfig
from snake.game import SnakeGame
from snake.game_objects.factories import (
    FoodFactory,
    FoodHandlerFactory,
    SnakeFactory,
    SnakeHandlerFactory,
)
from snake.pygame_interface.initializer import initialize_pygame
from snake.validators import ConfigValidator

if __name__ == "__main__":
    ConfigValidator.register_validator(*WindowConfig.get_all_validators(), *GameConfig.get_all_validators())
    ConfigValidator.validate_all()

    window_configuration = WindowConfig.from_dynaconf()
    snake_configuration = GameConfig.from_dynaconf()

    with initialize_pygame():
        game = SnakeGame(
            window_config=window_configuration,
            snake_config=snake_configuration,
            snake_handler=SnakeHandlerFactory(
                snake=SnakeFactory(
                    window_config=window_configuration,
                    snake_config=snake_configuration,
                ).create_snake()
            ).create_snake_handler(),
            food_handler=FoodHandlerFactory(
                food=FoodFactory(window_config=window_configuration, snake_config=snake_configuration).create_food(),
                window_config=window_configuration,
            ).create_food_handler(),
        )

        while game.is_not_over():
            game.run()

        score = game.get_score()
        print("Score", score)
