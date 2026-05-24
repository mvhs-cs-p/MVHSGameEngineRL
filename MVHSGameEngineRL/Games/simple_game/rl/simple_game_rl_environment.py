
import torch
from MVHSGameEngineML import RLEnvironment, Mode, EngineConfig

from Games.simple_game.src import config
from MVHSGameEngineML.src.core.config import TrainingStatus


class SimpleGameRLEnvironment(RLEnvironment):
    """
    This class defines the reinforcement learning environment for the Simple Game. It connects the actual Simple Game
    to the training systems. The class is responsible for the following:
        - Get observations from the game (get the game's state)
        - Step the game forward and see the result
        - Compute how the agent is reward/penalized for actions that are taken

    """



    def __init__(self, world, mode, headless_training = True):
        super().__init__(world, mode)
        self.mode = mode
        self.world = world
        self.headless_training = headless_training
        self.step_count = 0
        self.max_steps = config.MAX_STEPS

        # Define any game/environment states here that must persist across steps
        self.last_distance_to_goal = None


    def restart(self):
        """
        Restarts the environment for a new training episode
        """
        self.world.restart()
        self.step_count = 0

        # Reset any game/environment states here for next episode
        self.last_distance_to_goal = None


    def get_observation(self):
        """
        Get the observation from the game. Returns a dictionary of relevant game information used for training
        """

        player = self.world.player
        goal = self.world.goal

        return {
            "goal_pos" : goal.pos,
            "player_pos" : player.pos,
            "player_vel" : player.vel
        }


    def get_observation_tensor(self):
        """
        Convent raw game observation to a normalized PyTorch tensor used for the neural network.

        All values should be normalized between -1 and 1, or 0 and 1. Values found in the config file can be used
        to normalize them.

        Remember when defining the number of observation in the returned tensor it must match the number of inputs
        defined in the neural network policy defined in this games policy_net.py
        """

        # Get raw observation from the game
        observation = self.get_observation()
        goal_x, goal_y = observation["goal_pos"]
        player_x, player_y = observation["player_pos"]
        player_vel_x, player_vel_y = observation["player_vel"]

        # Normalize player velocity between -1 and 1 (roughly)
        player_vel_x /= config.PLAYER_MAX_VEL
        player_vel_y /= config.PLAYER_MAX_VEL

        # Get vector form player to goal
        player_to_goal_x = goal_x - player_x
        player_to_goal_y = goal_y - player_y

        # Normalize vector from player to goal
        player_to_goal_x /= config.WINDOW_WIDTH
        player_to_goal_y /= config.WINDOW_HEIGHT

        observations_tensor = torch.tensor([player_to_goal_x, player_to_goal_y, player_vel_x, player_vel_y], dtype=torch.float32)
        return observations_tensor


    def step(self, action):
        """
        Agent applies action, advance game state.

        This method must return a dictionary containing the following keys:
        - reward: how good or bad the result of the action was
        - steps_taken: how many steps the agent took, this may be more than 1, see ACTION_REPEAT in game config file
        - status: status after the step(s). Must be value from TrainingStatus (TRAINING, TIMEOUT, SUCCESS, GAME_OVER)
        """

        self.step_count += 1

        # Apply the action to the player in the game world
        self.world.player.apply_action(action)

        # Advance the game simulation by one tick (frame)
        self.world.tick(EngineConfig.fixed_dt)

        # Render the current game state. This method is defined in the base class.
        # If mode == Mode.AI_TRAIN_HEADLESS the game will not be rendered.
        self.render()

        # Advance the game simulation by addition ticks(frames) as defined by ACTION_REPEAT in game config file
        for _ in range(config.ACTION_REPEAT):
            self.world.tick(EngineConfig.fixed_dt)
            self.step_count += 1
            self.render()

        # Get new game world observation after applying the action and advancing the game simulation.
        observation = self.get_observation()
        current_distance_to_goal = observation["player_pos"].distance_to(observation["goal_pos"])
        game_won = self.world.game_won

        # Get the reward based on the observation states
        reward = self.compute_reward(game_won, current_distance_to_goal)

        self.last_distance_to_goal = current_distance_to_goal

        # Determine status episode status
        status = TrainingStatus.TRAINING
        if self.step_count > config.MAX_STEPS:
            status = TrainingStatus.TIMEOUT
        elif game_won:
            status = TrainingStatus.SUCCESS

        return {
            "reward": reward,
            "status": status
        }


    def compute_reward(self, game_won, current_distance_to_goal):
        """
        Compute the reward the for the current step.
        """
        if game_won:
            return 100

        if self.last_distance_to_goal is None:
            return -0.01

        distance_to_goal_change = (self.last_distance_to_goal - current_distance_to_goal) * 0.01
        being_alive_penality = -0.01
        return distance_to_goal_change + being_alive_penality


