from Games.flappy_bat.rl.flappybat_rl_environment import FlappyBatRLEnvironment
from Games.flappy_bat.rl.policy_net import FlappyBatPolicyNet
from Games.flappy_bat.src import config
from Games.flappy_bat.src.flappy_bat_world import FlappyBatGameWorld
from MVHSGameEngineML import Mode, AgentTrainer, AgentPlayer
from MVHSGameEngineML.src.rl import TrainingGUI


mode = config.MODE


if __name__ == '__main__':

    # Play game as a human (No AI)
    if mode == Mode.HUMAN_PLAY:

        world = FlappyBatGameWorld(mode=mode)
        world.run_world()

    # Train the AI, displays headless training dashboard
    elif mode == Mode.AI_TRAIN_HEADLESS:

        policy_network = FlappyBatPolicyNet()
        rl_environment = FlappyBatRLEnvironment(FlappyBatGameWorld(mode=mode), mode=mode)
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
        policy_network = FlappyBatPolicyNet()
        rl_environment = FlappyBatRLEnvironment(FlappyBatGameWorld(mode=mode), mode=mode, headless_training=False)

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
        policy_network = FlappyBatPolicyNet()
        rl_environment = FlappyBatRLEnvironment(FlappyBatGameWorld(mode=mode), mode=mode, headless_training=False)

        agent_player_config = {
            "policy_network": policy_network,
            "environment": rl_environment,
            "policy_file": config.PLAY_POLICY_FILE_PATH,
        }

        agent_player = AgentPlayer(agent_player_config)
        agent_player.play(episodes=100)














# import random
# import pygame
# from enum import Enum
#
# from Games.flappy_bat.src.player import FlappyBatPlayer
# from Games.flappy_bat.src.hud import HUD
# from MVHSGameEngineML import (
#     AABBCollider,
#     GameObject, Player, World, Mode,
#     PhysicsBody,
#     KeyInputType,
#     UIText, UIButton,
#     Prefabs, EventSystem
# )
#
# WINDOW_WIDTH = 1200
# WINDOW_HEIGHT = 800
#
# class GameState(Enum):
#     WAITING_TO_START = 0
#     PLAYING = 1
#     GAME_OVER = 2
#     WON = 3
#
#
# class FlappyBatGameWorld(World):
#     def __init__(self, mode=Mode.HUMAN_PLAY):
#         super().__init__(mode)
#         self.mode = mode
#         self.total_world_length = WINDOW_WIDTH * 10
#
#         self.player = FlappyBatPlayer(100, WINDOW_HEIGHT / 2)
#         self.game_state = GameState.PLAYING
#         self.score = 0
#         self.physics_system.debug = True
#
#         self.create_world(WINDOW_WIDTH, WINDOW_HEIGHT)
#
#         self.hud = None
#         if mode != Mode.AI_TRAIN_HEADLESS:
#             self.hud = HUD(self, WINDOW_WIDTH, WINDOW_HEIGHT)
#
#
#     def world_to_start(self):
#
#         self.add_game_object(self.player)
#         self.build_world()
#         # self.event_system.subscribe("on_player_ready_to_start", self.player_start)
#         self.event_system.subscribe("on_player_collision", self.player_collision)
#         self.event_system.subscribe("on_player_restart_ready", self.restart)
#
#
#     def build_world(self):
#         white_color = (255, 255, 255)
#
#         bottom = Prefabs.wall_top_left(0, WINDOW_HEIGHT - 10, self.total_world_length, 10, white_color)
#         self.add_game_object(bottom)
#         top = Prefabs.wall_top_left(0, 0, self.total_world_length, 10, white_color)
#         self.add_game_object(top)
#
#         start_x_pos = 300
#         barrier_width = 80
#         barrier_horizontal_gap = 280
#         barrier_vertical_gap = 250
#         random.seed(50)
#         for i in range(int(self.total_world_length * 0.90 / barrier_horizontal_gap)):
#
#             random_gap_center = random.uniform(0.35, 0.8)
#             gap_center = int(WINDOW_HEIGHT * random_gap_center)
#
#             x_pos = start_x_pos + i * barrier_horizontal_gap
#
#             top_barrier = Prefabs.wall_top_left(x_pos, 0, barrier_width, gap_center - barrier_vertical_gap / 2, white_color)
#             self.add_game_object(top_barrier)
#
#             bottom_barrier = Prefabs.wall_bottom_left(x_pos, WINDOW_HEIGHT, barrier_width,
#                                                       WINDOW_HEIGHT - gap_center - barrier_vertical_gap / 2, white_color)
#             self.add_game_object(bottom_barrier)
#
#     # def player_start(self):
#     #     self.game_state = GameState.PLAYING
#
#
#     def player_collision(self):
#         self.game_state = GameState.GAME_OVER
#         if self.hud is not None:
#             self.hud.set_game_over_visible(True)
#         self.game_state = GameState.GAME_OVER
#
#
#     def update_frame(self, dt):
#         super().update_frame(dt)
#         player_x_pos = self.player.pos.x
#         if player_x_pos > 300 and self.camera is not None:
#             self.camera.follow_target_pos(pygame.Vector2(player_x_pos + 300, WINDOW_HEIGHT / 2))
#
#         if self.game_state == GameState.PLAYING:
#             self.score = round(self.world_time, 1) * 10
#             #print(self.score)
#
#     def restart(self):
#         super().restart()
#         if self.camera is not None:
#             self.camera.pos = pygame.Vector2(0, 0)
#         if self.hud is not None:
#             self.hud.set_game_over_visible(False)
#         self.game_state = GameState.PLAYING
#
#
# if __name__ == "__main__":
#     world = FlappyBatGameWorld(mode = Mode.HUMAN_PLAY)
#     world.run_world()