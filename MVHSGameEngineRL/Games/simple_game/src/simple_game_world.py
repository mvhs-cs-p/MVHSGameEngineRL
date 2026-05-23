import pygame
import random

from Games.simple_game.src import config
from Games.simple_game.src.goal import Goal
from Games.simple_game.src.hud import HUD
from Games.simple_game.src.player import Player
from MVHSGameEngineML import World, Mode, Prefabs, UIButton, ImageCache
from MVHSGameEngineML.src.rendering.ui.ui_overlay import UIButtonImage


class SimpleGameWorld(World):
    def __init__(self, mode=Mode.HUMAN_PLAY):
        super().__init__(mode)
        self.game_name = config.GAME_NAME
        self.mode = mode
        self.background_color = (220, 240, 255)
        self.player = Player(0, 0)
        self.goal = Goal(int(config.WINDOW_WIDTH * 0.8), config.WINDOW_HEIGHT // 2)
        self.restart_button = None
        self.create_world(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.game_won = False

        if self.mode != Mode.AI_TRAIN_HEADLESS:
            self.hud = HUD(self)


    def world_to_start(self):

        self.set_start_positions()
        self.add_game_object(self.goal)
        self.add_game_object(self.player)

        walls = Prefabs.border_walls(config.WINDOW_WIDTH, config.WINDOW_HEIGHT,
                                     collision_layer=config.LAYER_WALL, collision_mask=config.LAYER_PLAYER, draw_debug = config.DRAW_PHYSICS_DEBUG)
        self.add_game_objects(*walls)

        self.event_system.subscribe("on_player_reach_goal", self.player_reached_goal)


    def get_random_start_position(self):
        x = int(random.uniform(config.WINDOW_WIDTH * 0.1, config.WINDOW_WIDTH * 0.9))
        y = int(random.uniform(config.WINDOW_HEIGHT * 0.1, config.WINDOW_HEIGHT * 0.9))
        return pygame.Vector2(x, y)


    def set_start_positions(self):
        positions_set = False
        while not positions_set:
            player_start_position = self.get_random_start_position()
            goal_start_position = self.get_random_start_position()
            positions_set = player_start_position.distance_to(goal_start_position) > int(config.WINDOW_HEIGHT * 0.8)
            if positions_set:
                self.player.pos = player_start_position
                self.goal.pos = goal_start_position


    def player_reached_goal(self):
        self.game_won = True


    def restart(self):
        super().restart()
        self.set_start_positions()
        self.game_won = False
        if self.mode != Mode.AI_TRAIN_HEADLESS:
            self.hud.hide_game_over()

