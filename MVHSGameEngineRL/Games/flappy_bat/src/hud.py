import pygame

from Games.flappy_bat.src import config
from MVHSGameEngineML import UIText, UIPanel, ImageCache, UIButtonImage


class HUD:
    def __init__(self, world):
        self.world = world
        self.world_ui_overlay = world.ui_overlay

        self.restart_button_image = ImageCache.load_image(config.IMAGES_DIR / "Restart_Button.png", default_scale=0.85)

        self.game_over_text = self.score_text = UIText("Game Over", pygame.Vector2(config.WINDOW_WIDTH // 2, int(config.WINDOW_HEIGHT * 0.3)),
                                                       150, pygame.Color(245, 245, 235), visible=False, pos_mode="center", font_name="Roboto")
        self.world_ui_overlay.add_component(self.game_over_text)

        self.restart_button = UIButtonImage(self.restart_button_image, self.on_restart_button_clicked, pygame.Vector2(config.WINDOW_WIDTH // 2, int(config.WINDOW_HEIGHT * 0.65)), visible=False)
        self.world_ui_overlay.add_component(self.restart_button)

        self.world.event_system.subscribe("on_player_collision", self.handle_on_player_collision)
        self.world.event_system.subscribe("on_player_won", self.handle_on_player_won)


    def update(self, player_score):
        if not self.world.game_over:
            self.score_text.set_text(f"{int(player_score)}")


    def handle_on_player_collision(self):
        self.game_over_text.set_text("Game Over")
        self.game_over_text.visible = True
        self.restart_button.visible = True


    def handle_on_player_won(self):
        self.game_over_text.set_text("Success")
        self.game_over_text.visible = True
        self.restart_button.visible = True


    def hide_game_over(self):
        self.restart_button.visible = False
        self.game_over_text.visible = False


    def on_restart_button_clicked(self):
        self.hide_game_over()
        self.world.restart()