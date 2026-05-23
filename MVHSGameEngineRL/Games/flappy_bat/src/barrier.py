import pygame

from Games.flappy_bat.src import config
from MVHSGameEngineML import GameObject, PhysicsBody, AABBCollider, Mode, ImageCache


class Barrier(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.physics_body = PhysicsBody(self)
        self.collider = AABBCollider(self, self.width, self.height)
        self.collider.draw_debug = config.DRAW_PHYSICS_DEBUG
        self.physics_body.collision_layer = config.LAYER_BARRIER
        self.physics_body.collision_mask = config.LAYER_PLAYER
        self.physics_body.is_static = True
        self.sprite = None



    def draw(self, renderer):
        if renderer is None:
            return

        # Outline
        renderer.draw_rect_center(self.pos, pygame.Vector2(self.width, self.height), (251, 146, 60))

        # Fill
        renderer.draw_rect_center(self.pos, pygame.Vector2(self.width-5, self.height-5), (110, 55, 35))