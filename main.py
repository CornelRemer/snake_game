from snake.agents import AIAgent, UserAgent
from snake.config import GameConfig, WindowConfig, settings
from snake.game import SnakeGameFactory
from snake.pygame_interface.initializer import initialize_pygame
from snake.validators import ConfigValidator

agents = {"USER": UserAgent, "AI": AIAgent}

if __name__ == "__main__":
    ConfigValidator.register_validator(*WindowConfig.get_all_validators(), *GameConfig.get_all_validators())
    ConfigValidator.validate_all()

    window_configuration = WindowConfig.from_dynaconf()
    game_configuration = GameConfig.from_dynaconf()

    with initialize_pygame():
        agent = agents[settings["agent_type"]](
            game_factory=SnakeGameFactory(
                window_configuration=window_configuration, game_configuration=game_configuration
            )
        )

        while agent.wants_to_play():
            agent.play_game()

        score = agent.get_score()
        print("Score", score)
