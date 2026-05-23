import pygame

from MVHSGameEngineML.src.collision.aabb_collider import AABBCollider
from MVHSGameEngineML.src.core.game_object import GameObject
from MVHSGameEngineML.src.physics.physics_body import PhysicsBody



class Wall(GameObject):
    def __init__(self, x, y, width, height, color, collision_layer = 0, collision_mask = 0, draw_debug = False):
        super().__init__(x, y)
        self.physics_body = PhysicsBody(self)
        self.physics_body.is_static = True
        self.physics_body.collision_layer = collision_layer
        self.physics_body.collision_mask = collision_mask
        self.width = width
        self.height = height
        self.collider = AABBCollider(self, self.width, self.height)
        self.collider.draw_debug = draw_debug
        self.color = color


    def draw(self, renderer):
        if renderer is None:
            return

        renderer.draw_rect_center(self.pos, pygame.Vector2(self.width, self.height), self.color)




class Prefabs:


    @staticmethod
    def wall(x, y, width, height, color):
        wall = Wall(int(x), int(y), int(width), int(height), color)
        return wall

    @staticmethod
    def wall_top_left(x, y, width, height, color):

        x_center = x + width/2
        y_center = y + height/2

        wall = Wall(x_center, y_center, width, height, color)
        return wall

    @staticmethod
    def wall_bottom_left(x, y, width, height, color):
        x_center = x + width/2
        y_center = y - height/2

        wall = Wall(x_center, y_center, width, height, color)
        return wall


    @staticmethod
    def border_walls(window_width, window_height, wall_width_half_thickness=10, color = (255, 115, 0), collision_layer = 0, collision_mask = 0, draw_debug = False):
        left_wall = Wall(0, int(window_height/2), wall_width_half_thickness, window_height, color, collision_layer, collision_mask, draw_debug)
        right_wall = Wall(window_width, int(window_height/2), wall_width_half_thickness, window_height, color, collision_layer, collision_mask, draw_debug)
        top_wall = Wall(int(window_width/2), 0, window_width, wall_width_half_thickness, color, collision_layer, collision_mask, draw_debug)
        bottom_wall = Wall(int(window_width/2), window_height, window_width, wall_width_half_thickness, color, collision_layer, collision_mask, draw_debug)
        return [left_wall, right_wall, top_wall, bottom_wall]

    @staticmethod
    def static_block(x, y, width, height, color):
        wall = Wall(x, y, width, height, color)
        return wall