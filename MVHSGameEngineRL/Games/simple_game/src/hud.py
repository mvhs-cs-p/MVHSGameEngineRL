import pygame

from Games.simple_game.src import config
from MVHSGameEngineML import UIText, UIPanel, ImageCache, UIButtonImage


class HUD:
    def __init__(self, world):
        self.world = world
        self.world_ui_overlay = world.ui_overlay

        self.restart_button_image = ImageCache.load_image(config.IMAGES_DIR / "Restart_Button.png", default_scale=0.85)

        self.success_text = self.score_text = UIText("Success", pygame.Vector2(config.WINDOW_WIDTH // 2, int(config.WINDOW_HEIGHT * 0.3)),
                                                       150, pygame.Color(22, 101, 52), visible=False, pos_mode="center", font_name="Roboto")
        self.world_ui_overlay.add_component(self.success_text)

        self.restart_button = UIButtonImage(self.restart_button_image, self.on_restart_button_clicked, pygame.Vector2(config.WINDOW_WIDTH // 2, int(config.WINDOW_HEIGHT * 0.65)), visible=False)
        self.world_ui_overlay.add_component(self.restart_button)

        self.world.event_system.subscribe("on_player_reach_goal", self.handle_on_player_won)


    def handle_on_player_won(self):
        self.success_text.visible = True
        self.restart_button.visible = True


    def hide_game_over(self):
        self.restart_button.visible = False
        self.success_text.visible = False


    def on_restart_button_clicked(self):
        self.hide_game_over()
        self.world.restart()