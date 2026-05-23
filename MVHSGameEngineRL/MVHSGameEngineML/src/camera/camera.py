import pygame

from MVHSGameEngineML.src.core.game_object import GameObject

class Camera:
    def __init__(self, viewport_width, viewport_height):
        self.pos = pygame.Vector2(0, 0)     # Top-Left of view in world space
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    def world_to_screen(self, world_pos: pygame.Vector2) -> pygame.Vector2:

        """
        map world coordinates to screen coordinates
        """

        return pygame.Vector2(
            world_pos.x - self.pos.x,
            world_pos.y - self.pos.y
        )


    def screen_to_world(self, screen_pos: pygame.Vector2) -> pygame.Vector2:

        """
        map screen coordinates to world coordinates
        """

        return pygame.Vector2(
            screen_pos.x + self.pos.x,
            screen_pos.y + self.pos.y
        )


    def follow_target_pos(self, target_pos: pygame.Vector2):

        """
        position camera so that it is centered at target_pos
        """

        self.pos.x = target_pos.x - round(self.viewport_width * 0.5)
        self.pos.y = target_pos.y - round(self.viewport_height * 0.5)


    def follow_game_object(self, game_object: GameObject):

        """
        position camera so that it is centered at game_objects position
        """

        self.pos.x = game_object.pos.x - round(self.viewport_width * 0.5)
        self.pos.y = game_object.pos.y - round(self.viewport_height * 0.5)


    # def cull_game_object(self, game_object: GameObject):
    #
    #     """
    #     (NOT USED)
    #     This method is probably not needed. (pygame has some internal culling)
    #     :param game_object:
    #     :return:
    #     """
    #
    #     camera_left = self.pos.x
    #     camera_right = self.pos.x + self.viewport_width
    #     camera_top = self.pos.y
    #     camera_bottom = self.pos.y + self.viewport_height
    #
    #     if game_object.collider is not None:
    #         collider_rect = game_object.collider.get_rect()
    #         game_object_left = collider_rect.left
    #         game_object_right = collider_rect.right
    #         game_object_top = collider_rect.top
    #         game_object_bottom = collider_rect.bottom
    #     elif game_object.width > 0 and game_object.height > 0:
    #         game_object_left = game_object.pos.x - round(game_object.width * 0.5)
    #         game_object_right = game_object.pos.x + round(game_object.width * 0.5)
    #         game_object_top = game_object.pos.y - round(game_object.height * 0.5)
    #         game_object_bottom = game_object.pos.y + round(game_object.height * 0.5)
    #     else:
    #         return False
    #
    #     if game_object_right < camera_left:
    #         return True
    #     elif game_object_left > camera_right:
    #         return True
    #     elif game_object_top > camera_bottom:
    #         return True
    #     elif game_object_bottom < camera_top:
    #         return True
    #
    #     return False
