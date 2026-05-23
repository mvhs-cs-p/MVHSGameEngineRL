import pygame
import random

from MVHSGameEngineML import GameObject, PhysicsBody, AABBCollider, Mode, ImageCache

from Games.simple_game.src import config

class Goal(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 100
        self.height = 100
        self.physics_body = PhysicsBody(self)
        self.physics_body.is_static = True
        self.physics_body.collision_layer = config.LAYER_GOAL
        self.physics_body.collision_mask = config.LAYER_PLAYER
        self.collider = AABBCollider(self, self.width-60, self.height-25)
        self.collider.draw_debug = config.DRAW_PHYSICS_DEBUG
        self.name = "goal"
        self.sprite = None


    def init(self):

        if self.world.mode != Mode.AI_TRAIN_HEADLESS:
            self.sprite = ImageCache.load_image(config.IMAGES_DIR / "goal.png", default_scale=0.5)


    def draw(self, renderer):

        if renderer is None:
            return

        renderer.draw_image(self.sprite, self.pos)

