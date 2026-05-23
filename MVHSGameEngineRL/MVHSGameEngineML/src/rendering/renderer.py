import pygame

from MVHSGameEngineML.src.rendering.ui.font_cache import FontCache
from MVHSGameEngineML.src.rendering.ui.ui_overlay import UIButton, UIText, UIImage
from MVHSGameEngineML.src.camera import Camera


class Renderer:
    def __init__(self, window, world, camera):
        self.window = window
        self.world = world
        self.camera = camera


    def draw_text(self, text: str, center: pygame.Vector2, size: int, color: pygame.Color, rot: float = 0.0, font_name="Comic Sans MS", bold=False, italic=False) -> None:

        """
        Draw a text using a center position. If drawing text as part of UI prefer draw_ui_text via UIOverlay.

        :param text: Text to draw
        :param size: size of the text
        :param color: RGB color of the text
        :param center: (x, y) screen position where the text will be centered
        :param rot: Rotation angle in degrees, positive values are counter-clockwise
        :param font_name: Name of system font
        """

        screen_pos = self.camera.world_to_screen(center)
        font = FontCache.get(font_name, size, bold=bold, italic=italic)
        text_surface = font.render(text, True, color)
        if rot != 0:
            text_surface = pygame.transform.rotate(text_surface, rot)

        font_rect = text_surface.get_rect(center=screen_pos)
        self.window.blit(text_surface, font_rect)


    def draw_ui_text(self, ui_text: UIText) -> None:

        """
        Draw text using a UIText object.
        """

        self.window.blit(ui_text.text.text_surface, ui_text.text.font_rect)


    def draw_ui_button(self, ui_button: UIButton) -> None:

        """
        Draw button using a UIButton object.
        """

        pygame.draw.rect(self.window, ui_button.button_color, ui_button.button_rect, ui_button.corner_radius)
        self.window.blit(ui_button.text.text_surface, ui_button.text.font_rect)

    def draw_ui_panel(self, ui_panel) -> None:

        self.window.blit(ui_panel.surface, ui_panel.panel_rect)


    def draw_image(self, surface: pygame.Surface, center: pygame.Vector2, rot: float = 0, scale: float = 1) -> None:
        """
        Draw an image using a center position.

        :param window: The screen surface to draw on
        :param surface: The original surface (image) to draw
        :param center: position on the screen (window) where the center of the image (surface) will be placed
        :param rot: Rotation angle in degrees, positive values are counter-clockwise
        :param scale: Scale factor (1 = original size, smaller scale factor = smaller image)
        :return: None
        """


        screen_pos = self.camera.world_to_screen(center)
        image = pygame.transform.rotozoom(surface, rot, scale)
        rect = image.get_rect(center=screen_pos)
        self.window.blit(image, rect)

    def draw_backdrop(self, surface: pygame.Surface):
        image = pygame.transform.rotozoom(surface, 0, 1)
        rect = image.get_rect(topleft=(0, 0))

        self.window.blit(image, rect)


    def draw_ui_image(self, surface: pygame.Surface, pos: pygame.Vector2, centered = False, rot: float = 0, scale: float = 1) -> None:
        image = pygame.transform.rotozoom(surface, rot, scale)
        if centered:
            rect = image.get_rect(center=(int(pos.x), int(pos.y)))
        else:
            rect = image.get_rect(topleft=(int(pos.x), int(pos.y)))
        self.window.blit(image, rect)


    def draw_rect_center(self, center: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, rot=0.0, border_width=0) ->None:

        """
        Draw a rectangle center using a center position, optional rotation, and scale.

        :param center: screen position where the rectangle will be centered
        :param size: size of the rectangle in pixels
        :param color: color of the rectangle
        :param rot: rotation angle in degrees, positive values are counter-clockwise
        :param border_width: 0 draws a filled rect. >0 draws an outline of that thickness.
        """
        screen_pos = self.camera.world_to_screen(center)
        surface_size = (int(size.x), int(size.y))
        temp_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, pygame.Rect(0, 0,size.x, size.y), border_width)
        rotated = pygame.transform.rotate(temp_surface, rot)
        rect = rotated.get_rect(center=(round(screen_pos.x), round(screen_pos.y)))
        self.window.blit(rotated, rect)


    def draw_rect_top_left(self, top_left: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, rot=0.0, border_width=0) -> None:
        """
        Draw a rectangle using a top-left position.

        :param top_left: screen position of the top-left corner
        :param size: size of the rectangle in pixels
        :param color: color of the rectangle
        :param rot: rotation angle in degrees, positive values are counter-clockwise
        :param border_width: 0 draws a filled rect. >0 draws an outline of that thickness.
        """
        screen_pos = self.camera.world_to_screen(top_left)
        surface_size = (int(size.x), int(size.y))
        temp_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, pygame.Rect(0, 0, size.x, size.y), border_width)
        rotated = pygame.transform.rotate(temp_surface, rot)
        rect = rotated.get_rect(topleft=(round(screen_pos.x), round(screen_pos.y)))
        self.window.blit(rotated, rect)


    def draw_rect_bottom_left(self, bottom_left: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, rot=0.0, border_width=0) -> None:
        """
        Draw a rectangle using a bottom-left position.

        :param bottom_left: screen position of the bottom-left corner
        :param size: size of the rectangle in pixels
        :param color: color of the rectangle
        :param rot: rotation angle in degrees, positive values are counter-clockwise
        :param border_width: 0 draws a filled rect. >0 draws an outline of that thickness.
        """
        screen_pos = self.camera.world_to_screen(bottom_left)
        surface_size = (int(size.x), int(size.y))
        temp_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, pygame.Rect(0, 0, size.x, size.y), border_width)
        rotated = pygame.transform.rotate(temp_surface, rot)
        rect = rotated.get_rect(bottomleft=(round(screen_pos.x), round(screen_pos.y)))
        self.window.blit(rotated, rect)


    def draw_rect_top_right(self, top_right: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, rot=0.0, border_width=0) -> None:
        """
        Draw a rectangle using a top-right position.

        :param top_right: screen position of the top-right corner
        :param size: size of the rectangle in pixels
        :param color: color of the rectangle
        :param rot: rotation angle in degrees, positive values are counter-clockwise
        :param border_width: 0 draws a filled rect. >0 draws an outline of that thickness.
        """
        screen_pos = self.camera.world_to_screen(top_right)
        surface_size = (int(size.x), int(size.y))
        temp_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, pygame.Rect(0, 0, size.x, size.y), border_width)
        rotated = pygame.transform.rotate(temp_surface, rot)
        rect = rotated.get_rect(topright=(round(screen_pos.x), round(screen_pos.y)))
        self.window.blit(rotated, rect)


    def draw_rect_bottom_right(self, bottom_right: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, rot=0.0, border_width=0) -> None:
        """
        Draw a rectangle using a bottom-right position.

        :param bottom_right: screen position of the bottom-right corner
        :param size: size of the rectangle in pixels
        :param color: color of the rectangle
        :param rot: rotation angle in degrees, positive values are counter-clockwise
        :param border_width: 0 draws a filled rect. >0 draws an outline of that thickness.
        """
        screen_pos = self.camera.world_to_screen(bottom_right)
        surface_size = (int(size.x), int(size.y))
        temp_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, pygame.Rect(0, 0, size.x, size.y), border_width)
        rotated = pygame.transform.rotate(temp_surface, rot)
        rect = rotated.get_rect(bottomright=(round(screen_pos.x), round(screen_pos.y)))
        self.window.blit(rotated, rect)


    def draw_ellipse_centered(self, center: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, rot=0.0, border_width=0) -> None:

        """
        Draw an ellipse centered using a center position, optional rotation, and scale.

        :param center: screen position where the ellipse will be centered
        :param size: size of the ellipse in pixels
        :param color: color of the ellipse
        :param rot: rotation angle in degrees, positive values are counter-clockwise
        :param border_width: 0 draws a filled ellipse. >0 draws an outline of that thickness.
        """

        screen_pos = self.camera.world_to_screen(center)
        surface_size = (int(size.x), int(size.y))
        temp_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        ellipse_rect = pygame.Rect(0, 0, int(size.x), int(size.y))
        pygame.draw.ellipse(temp_surface, color, ellipse_rect, border_width)
        rotated = pygame.transform.rotate(temp_surface, rot)
        rect = rotated.get_rect(center=(round(screen_pos.x), round(screen_pos.y)))
        self.window.blit(rotated, rect)


    def draw_line(self, start: pygame.Vector2, end: pygame.Vector2, color=(255, 255, 255), width=1) -> None:
        start_screen_pos = self.camera.world_to_screen(start)
        end_screen_pos = self.camera.world_to_screen(end)
        pygame.draw.line(self.window, color, start_screen_pos, end_screen_pos, width)

    def draw_grid(self, top_left: pygame.Vector2, height, width, horizontal_space: float, vertical_space) -> None:

        num_horizontal_lines = int(height / vertical_space) + 3
        num_vertical_lines = int(width / horizontal_space) + 3

        # Horizontal lines
        for i in range(num_horizontal_lines):
            y_offset = i * vertical_space

            start = top_left + pygame.Vector2(0, y_offset)
            end = start + pygame.Vector2(width, 0)

            self.draw_line(start, end, color=(124, 23, 255), width=1)

        # Vertical lines
        for i in range(num_vertical_lines):
            x_offset = i * horizontal_space

            start = top_left + pygame.Vector2(x_offset, 0)
            end = start + pygame.Vector2(0, height)

            self.draw_line(start, end, color=(124, 23, 255), width=1)





