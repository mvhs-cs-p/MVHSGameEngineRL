import pygame
import torch

from Games.flappy_bat.src import config
from MVHSGameEngineML import RLEnvironment, Mode, EngineConfig
from MVHSGameEngineML.src.core.config import TrainingStatus

"""
Flappy Bat RL Environment

This file defines the reinforcement learning environment for Flappy Bat game. It connects the actual Flappy Bat game
to the training systems. The class is responsible for the following:
    - Get observations from the game (get the game's state)
    - Step the game forward and see the result
    - Compute how the agent is reward/penalized for actions that are taken

"""

class FlappyBatRLEnvironment(RLEnvironment):
    def __init__(self, world, mode, headless_training = True):
        super().__init__(world, mode)
        self.mode = mode
        self.world = world
        self.headless_training = headless_training
        self.step_count = 0
        self.max_steps = config.MAX_STEPS

        # Define any game/environment states here that must persist across steps
        # For example last_distance_to_goal


    def restart(self):
        """
        Restarts the environment for a new training episode
        """
        self.world.restart()
        self.step_count = 0

        # Reset any game/environment states here for next episode


    def get_observation(self):
        """
        Get the observation from the game. Returns a dictionary of relevant game information used for training
        """

        player = self.world.player

        return {
            "player_pos": player.pos,
            "player_vel" : player.vel,
            "player_traces" : player.get_line_traces()
        }

    def get_observation_tensor(self):
        """
        Convent raw game observation to a normalized PyTorch tensor used for the neural network.

        All values should be normalized between -1 and 1, or 0 and 1. Values found in the config file can be used
        to normalize them.

        Remember when defining the number of observation in the returned tensor it must match the number of inputs
        defined in the neural network policy defined in this games policy_net.py
        :return:
        """

        # Get raw observation from the game
        observation = self.get_observation()
        player_pos_x, player_pos_y = observation["player_pos"]
        player_vel_x, player_vel_y = observation["player_vel"]

        # Normalize player position between 0 and 1
        player_pos_y /= config.WINDOW_HEIGHT

        # Normalize player velocity between -1 and 1 (roughly)
        player_vel_y /= config.PLAYER_MAX_VEL

        # Normalize trace distances between 0 and 1 where,
        #   1 - trace from place does is not contacting anything
        #   0 - trace start position is contacting another object
        trace_distances = []
        for trace in observation["player_traces"]:
            trace_distances.append(trace / config.PLAYER_TRACE_DISTANCE)


        observation_values = [player_pos_y, player_vel_y]
        observation_values.extend(trace_distances)
        observation_tensor = torch.tensor(observation_values, dtype=torch.float)
        return observation_tensor


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

        # Advance the game simulation by addition ticks as defined by ACTION_REPEAT in game config file
        for _ in range(config.ACTION_REPEAT):
            self.world.tick(EngineConfig.fixed_dt)
            self.step_count += 1
            self.render()

        # Get new game world observation after applying the action and advancing the game simulation.
        game_over = self.world.game_over
        game_won = self.world.game_won

        reward = self.compute_reward(game_over, game_won)

        # Determine status episode status
        status = TrainingStatus.TRAINING
        if self.step_count > config.MAX_STEPS:
            status = TrainingStatus.TIMEOUT
        elif game_won:
            status = TrainingStatus.SUCCESS
        elif game_over:
            status = TrainingStatus.GAME_OVER

        return {
            "reward": reward,
            "status": status
        }


    def compute_reward(self, game_over, game_won):
        """
        Compute the reward the for the current step.
        """

        if game_won:
            return 100
        elif game_over:
            return -100
        else:
            return 0.1

