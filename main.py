from snake.agents import UserAgent
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
    game_configuration = GameConfig.from_dynaconf()

    with initialize_pygame():
        agent = UserAgent(
            game=SnakeGame(
                window_config=window_configuration,
                game_config=game_configuration,
                snake_handler=SnakeHandlerFactory(
                    snake=SnakeFactory(
                        window_config=window_configuration,
                        game_config=game_configuration,
                    ).create_snake()
                ).create_snake_handler(),
                food_handler=FoodHandlerFactory(
                    food=FoodFactory(window_config=window_configuration, game_config=game_configuration).create_food(),
                    window_config=window_configuration,
                ).create_food_handler(),
            ),
            window_configuration=window_configuration,
            game_configuration=game_configuration,
        )

        while agent.wants_to_play():
            agent.play_game()

        # score = game.get_score()
        # print("Score", score)
