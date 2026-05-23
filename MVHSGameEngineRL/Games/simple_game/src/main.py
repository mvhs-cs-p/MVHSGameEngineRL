
from Games.simple_game.rl.policy_net import SimpleGameAgentPolicyNet
from Games.simple_game.src import config
from Games.simple_game.src.simple_game_world import SimpleGameWorld
from MVHSGameEngineML import Mode, AgentPlayer, AgentTrainer
from Games.simple_game.rl.simple_game_rl_environment import SimpleGameRLEnvironment
from MVHSGameEngineML.src.rl import TrainingGUI

mode = config.MODE


if __name__ == "__main__":

    # Train the AI, displays headless training dashboard
    if mode == Mode.AI_TRAIN_HEADLESS:

        policy_network = SimpleGameAgentPolicyNet()
        rl_environment = SimpleGameRLEnvironment(SimpleGameWorld(mode=mode), mode=mode)
        training_gui_config = {
            "rl_environment": rl_environment,
            "policy_network": policy_network,
            "policy_dir" : config.POLICY_DIRECTORY,
            "game_name": config.GAME_NAME,
            "default_training_episodes" : config.DEFAULT_EPISODES,
            "default_learning_rate": config.DEFAULT_LEARNING_RATE,
            "default_exploration_bonus": config.DEFAULT_EXPLORATION_BONUS,
            "default_gamma": config.DEFAULT_GAMMA,
            "config_notes" : config.get_config_string_notes()
        }

        training_gui = TrainingGUI(training_gui_config)
        training_gui.run()

    # Train the AI in real time while rendering the game. (See training in action, not useful to train actual policy)
    elif mode == Mode.AI_TRAIN:

        policy_network = SimpleGameAgentPolicyNet()
        rl_environment = SimpleGameRLEnvironment(SimpleGameWorld(mode=mode), mode=mode)

        agent_trainer_config = {
            "policy": policy_network,
            "learning_rate": config.DEFAULT_LEARNING_RATE,
            "gamma": config.DEFAULT_GAMMA,
            "episodes": config.DEFAULT_EPISODES,
            "exploration_bonus": config.DEFAULT_EXPLORATION_BONUS,
            "environment": rl_environment,
        }
        agent_trainer = AgentTrainer(agent_trainer_config)
        agent_trainer.start_training()

    # AI plays the game using the policy file set in config.PLAY_POLICY_FILE
    elif mode == Mode.AI_PLAY:
        policy_network = SimpleGameAgentPolicyNet()
        rl_environment = SimpleGameRLEnvironment(SimpleGameWorld(mode=mode), mode=mode)

        agent_player_config = {
            "policy_network": policy_network,
            "environment": rl_environment,
            "policy_file": config.PLAY_POLICY_FILE_PATH,
        }

        agent_player = AgentPlayer(agent_player_config)
        agent_player.play(episodes=100)

    elif mode == Mode.HUMAN_PLAY:
        world = SimpleGameWorld(mode=mode)
        world.run_world()

