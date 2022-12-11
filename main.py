from snake.agents import AbstractAgentFactory
from snake.config import GameConfig, WindowConfig
from snake.pygame_interface.initializer import initialize_pygame
from snake.validators import ConfigValidator

if __name__ == "__main__":
    ConfigValidator.register_validator(*WindowConfig.get_all_validators(), *GameConfig.get_all_validators())
    ConfigValidator.validate_all()

    window_configuration = WindowConfig.from_dynaconf()
    game_configuration = GameConfig.from_dynaconf()

    with initialize_pygame():
        agent = AbstractAgentFactory(
            window_configuration=window_configuration,
            game_configuration=game_configuration,
        ).create_agent()

        while agent.wants_to_play():
            agent.play_game()

        score = agent.get_max_score()
        print("Max score", score)
