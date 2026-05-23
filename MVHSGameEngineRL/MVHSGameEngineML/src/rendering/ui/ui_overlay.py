
import pygame

from MVHSGameEngineML.src.rendering.image_cache import ImageCache
from MVHSGameEngineML.src.utilities.logger import Logger
from MVHSGameEngineML.src.rendering.ui.font_cache import FontCache


class UITextComponent:
    def __init__(self, text, pos: pygame.Vector2, size: int, color, font_name = "Comic Sans MS", bold = False, italic = False, rot = 0, pos_mode = "top_left"):
        self.color = color
        self.pos = pos
        self.rot = rot
        self.pos_mode = pos_mode
        self.font = FontCache().get(font_name, size, bold=bold, italic=italic)
        self.text_surface = None
        self.font_rect = None
        self.set_text(text)


    def set_text(self, text: str):
        self.text_surface = self.font.render(text, True, self.color)
        if self.rot != 0:
            self.text_surface = pygame.transform.rotate(self.text_surface, self.rot)

        pos = int(self.pos.x), int(self.pos.y)
        if self.pos_mode == "top_left":
            self.font_rect = self.text_surface.get_rect(topleft=(pos[0], pos[1]))
        elif self.pos_mode == "center":
            self.font_rect = self.text_surface.get_rect(center=(pos[0], pos[1]))
        else:
            Logger.log_error(self, f"Invalid pos_mode: ({self.pos_mode})")


class UIOverlayComponent:
    def __init__(self, visible=True, order=0):
        self.visible = visible
        self.order = order
        self.call_back = None

    def draw(self, renderer):
        pass


class UIPanel(UIOverlayComponent):
    def __init__(self, pos: pygame.Vector2, width: int, height: int, color: pygame.Color, rot=0, visible=True, order=0, pos_mode = "top_left"):
        super().__init__(visible, order)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill(color)

        if rot != 0:
            self.surface = pygame.transform.rotate(self.surface, rot)

        self.panel_rect = None
        if pos_mode == "top_left":
            self.panel_rect = self.surface.get_rect(topleft=(pos[0], pos[1]))
        elif pos_mode == "center":
            self.panel_rect = self.surface.get_rect(center=(pos[0], pos[1]))
        else:
            Logger.log_error(self, f"Invalid pos_mode: ({pos_mode})")

    def draw(self, renderer):
        renderer.draw_ui_panel(self)


class UIText(UIOverlayComponent):
    def __init__(self, text: str, pos: pygame.Vector2, size: int, color: pygame.Color, font_name = "Comic Sans MS", bold = False, italic = False, rot = 0, visible=True, order=0, pos_mode = "top_left"):
        super().__init__(visible, order)
        self.text = UITextComponent(text, pos, size, color, font_name, bold, italic, rot, pos_mode)

    def draw(self, renderer):
        if self.visible:
            renderer.draw_ui_text(self)

    def set_text(self, text: str):
        self.text.set_text(text)


class UIButton(UIOverlayComponent):
    def __init__(self, call_back, text, pos: pygame.Vector2, text_size: int, text_color, button_color, padding=(10, 10), corner_radius=0, font_name = "Comic Sans MS", bold = False, italic = False, rot = 0, visible=True, order=0):
        super().__init__(visible, order)
        self.text = UITextComponent(text, pos, text_size, text_color, font_name, bold, italic, rot)

        text_rect = self.text.text_surface.get_rect()
        self.button_width = text_rect.width + padding[0] * 2
        self.button_height = text_rect.height + padding[1] * 2
        self.button_rect = pygame.Rect(0, 0, round(self.button_width), round(self.button_height))
        self.button_rect.center = (round(pos.x), round(pos.y))
        self.button_color = button_color
        self.corner_radius = corner_radius
        self.call_back = call_back

    def draw(self, renderer):
        renderer.draw_ui_button(self)

class UIButtonImage(UIOverlayComponent):
    def __init__(self, image, call_back, pos: pygame.Vector2, rot=0, visible=True, order=0, pos_mode = "top_left"):
        super().__init__(visible, order)
        self.image = image
        self.pos = pos
        self.rot = rot
        self.call_back = call_back
        self.button_rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))

    def draw(self, renderer):
        renderer.draw_image(self.image, self.pos, self.rot)

class UIImage(UIOverlayComponent):
    def __init__(self, image, pos: pygame.Vector2, rot=0, visible=True, order=0, centered = False, scale=1):
        super().__init__(visible, order)
        self.image = image
        self.pos = pos
        self.rot = rot
        self.visible = visible
        self.centered = centered
        self.scale = scale

    def draw(self, renderer):
        renderer.draw_ui_image(self.image, self.pos, centered=self.centered, rot=self.rot, scale=self.scale)




class UIOverlay:
    def __init__(self, renderer):
        self.renderer = renderer
        self.ui_components = []


    def add_component(self, new_ui_component: UIOverlayComponent):

        """
        Add a new UI component to the UI overlay. Duplicate components same reference, are not added.
        If a new component is added ui_components are sorted based on order number
        """

        if new_ui_component not in self.ui_components:
            self.ui_components.append(new_ui_component)
            self.ui_components.sort(key=lambda x: x.order)


    def draw(self):

        """
        Draw UIOverlay to the screen.
        """

        for component in self.ui_components:
            if component.visible:
                component.draw(self.renderer)


    def process_input(self, event):

        """
        Process pygame mouse button down events as UI input events. UIButton callbacks
        are triggered if mose down event occurred over UIButton.
        :param event:
        :return:
        """

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos[0], event.pos[1]

            for component in reversed(self.ui_components):
                if component.visible and component.call_back is not None:

                    # TODO: Right the only UIComponent with a call_back is UI_Button.
                    #  will need to change below if another clickable UIComponent is added
                    if component.button_rect.collidepoint(mouse_pos):
                        component.call_back()




