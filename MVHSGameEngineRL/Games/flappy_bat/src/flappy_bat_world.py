import random
import pygame
from enum import Enum

from Games.flappy_bat.src import config
from Games.flappy_bat.src.barrier import Barrier
from Games.flappy_bat.src.player import FlappyBatPlayer
from Games.flappy_bat.src.hud import HUD
from MVHSGameEngineML import (
    AABBCollider,
    GameObject, Player, World, Mode,
    PhysicsBody,
    KeyInputType,
    UIText, UIButton,
    Prefabs, EventSystem, Logger
)





class FlappyBatGameWorld(World):
    def __init__(self, mode=Mode.HUMAN_PLAY):
        super().__init__(mode)
        self.mode = mode
        self.total_world_length = config.WINDOW_WIDTH * 15
        self.player = FlappyBatPlayer(100, config.WINDOW_HEIGHT // 2)
        self.barriers = []
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.physics_system.debug = True

        self.create_world(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.hud = None
        if mode != Mode.AI_TRAIN_HEADLESS:
            self.hud = HUD(self)


    def world_to_start(self):

        self.add_game_object(self.player)
        self.build_world()
        self.event_system.subscribe("on_player_collision", self.handle_on_player_collision)
        self.event_system.subscribe("on_player_won", self.handle_on_player_won)


    def handle_on_player_collision(self):
        self.game_over = True
        self.game_won = False


    def handle_on_player_won(self):
        self.game_over = True
        self.game_won = True


    def build_world(self):

        start_x_pos = 800
        # BARRIER_WIDTH = 80
        #barrier_horizontal_gap = 300
        #barrier_vertical_gap = 250

        if config.MIN_BARRIER_VERTICAL_GAP_CENTER > config.MAX_BARRIER_VERTICAL_GAP_CENTER:
            Logger.log_error(self, "Unable to build world, ensure MIN_BARRIER_VERTICAL_GAP_CENTER is less than MAX_BARRIER_VERTICAL_GAP_CENTER in config")

        for i in range(int(self.total_world_length * 0.90 /  config.BARRIER_HORIZONTAL_SPACING)):
            x_pos = start_x_pos + i * config.BARRIER_HORIZONTAL_SPACING

            random_gap_center = random.uniform(config.MIN_BARRIER_VERTICAL_GAP_CENTER, config.MAX_BARRIER_VERTICAL_GAP_CENTER)
            gap_center = int(config.WINDOW_HEIGHT * random_gap_center)

            top_barrier_height = gap_center - config.BARRIER_VERTICAL_SPACING // 2
            top_barrier = Barrier(x_pos + config.BARRIER_WIDTH // 2, top_barrier_height // 2, config.BARRIER_WIDTH, top_barrier_height)
            self.add_game_object(top_barrier)
            self.barriers.append(top_barrier)

            bottom_barrier_y = gap_center + config.BARRIER_VERTICAL_SPACING // 2
            bottom_barrier_height = config.WINDOW_HEIGHT - bottom_barrier_y
            bottom_barrier = Barrier(x_pos + config.BARRIER_WIDTH // 2, bottom_barrier_y + bottom_barrier_height // 2, config.BARRIER_WIDTH, bottom_barrier_height)
            self.add_game_object(bottom_barrier)
            self.barriers.append(bottom_barrier)


    def update_frame(self, dt):
        super().update_frame(dt)
        self.score = self.world_time

        if self.mode != Mode.AI_TRAIN_HEADLESS:
            player_x_pos = self.player.pos.x
            if player_x_pos > 300 and self.camera is not None:
                self.camera.follow_target_pos(pygame.Vector2(player_x_pos + 300, config.WINDOW_HEIGHT // 2))


    def restart(self):
        super().restart()

        for barrier in self.barriers:
            self._remove_game_object_internal(barrier)

        self.build_world()
        self.game_over = False
        self.game_won = False
        if self.mode != Mode.AI_TRAIN_HEADLESS:
            self.camera.pos = pygame.Vector2(0, 0)
            self.hud.hide_game_over()




