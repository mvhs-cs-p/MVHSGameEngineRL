

import pygame
from ..utilities.logger import Logger

class AABBCollider:
    def __init__(self, owner, width, height, offset_x=0, offset_y=0, is_trigger=False):
        self.owner = owner
        self.size = pygame.Vector2(width, height)
        self.offset = pygame.Vector2(offset_x, offset_y)
        self.is_trigger = is_trigger
        self.receive_hit_events = False
        #self.receive_overlap_events = False

        self.draw_debug = False
        self.draw_debug_color = (114, 255, 0)
        self.draw_debug_thickness = 1



    def get_rect(self) -> pygame.Rect:
        center = self.get_center_pos()
        rect = pygame.Rect(0, 0, int(self.size.x), int(self.size.y))
        rect.center = (round(center.x), round(center.y))
        return rect


    def get_center_pos(self):
        return pygame.Vector2(self.owner.pos.x + self.offset.x,
                            self.owner.pos.y + self.offset.y)

    def draw(self):
        if self.draw_debug:
            renderer = self.owner.world.renderer
            if renderer is None:
                Logger.log_error(self, "Trying to draw renderer not accessible")
                return

            renderer.draw_rect_center(self.get_center_pos(), self.size, self.draw_debug_color, 0, self.draw_debug_thickness)
