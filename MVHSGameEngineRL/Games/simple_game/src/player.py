import random
import pygame

from MVHSGameEngineML import (
    AABBCollider,
    GameObject,
    PhysicsBody,
    Mode, ImageCache
)

from Games.simple_game.src import config

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.physics_body = PhysicsBody(self)
        self.physics_body.drag_k = 2.6
        self.physics_body.max_vel = config.PLAYER_MAX_VEL
        self.physics_body.collision_layer = config.LAYER_PLAYER
        self.physics_body.collision_mask = config.LAYER_WALL & config.LAYER_GOAL
        self.physics_body.gravity_scale = 0
        self.width = 40
        self.height = 40
        self.collider = AABBCollider(self, self.width, self.height)
        self.collider.draw_debug = config.DRAW_PHYSICS_DEBUG
        self.collider.receive_hit_events = True
        self.sprite = None
        self.player_input_force = 800
        self.name = "Player"


    def init(self):

        if self.world.mode == Mode.HUMAN_PLAY:

            input_manager = self.world.player_input_manager
            input_manager.register_key_held(pygame.K_LEFT, self.move_left)
            input_manager.register_key_held(pygame.K_a, self.move_left)

            input_manager.register_key_held(pygame.K_RIGHT, self.move_right)
            input_manager.register_key_held(pygame.K_d, self.move_right)

            input_manager.register_key_held(pygame.K_UP, self.move_up)
            input_manager.register_key_held(pygame.K_w, self.move_up)

            input_manager.register_key_held(pygame.K_DOWN, self.move_down)
            input_manager.register_key_held(pygame.K_s, self.move_down)

        if self.world.mode != Mode.AI_TRAIN_HEADLESS:
            self.sprite = ImageCache.load_image(config.IMAGES_DIR / "player.png", default_scale=0.25)


    def move_left(self):
        self.physics_body.add_force(pygame.Vector2(-1, 0) * self.player_input_force)


    def move_right(self):
        self.physics_body.add_force(pygame.Vector2(1, 0) * self.player_input_force)


    def move_up(self):
        self.physics_body.add_force(pygame.Vector2(0, -1) * self.player_input_force)


    def move_down(self):
        self.physics_body.add_force(pygame.Vector2(0, 1) * self.player_input_force)


    def apply_action(self, action):
        # Action == 0 for NOOP
        match action:
            case 1: self.move_left()
            case 2: self.move_right()
            case 3: self.move_up()
            case 4: self.move_down()


    def on_collision(self, other_game_object):
        if other_game_object.name == "goal":
            self.physics_body.set_enabled(False)
            self.world.event_system.broadcast("on_player_reach_goal")


    def draw(self, renderer):
        if renderer is None:
            return

        renderer.draw_image(self.sprite, self.pos)


    def restart(self):
        self.physics_body.set_enabled(True)






