import math

import pygame

from Games.flappy_bat.src import config
from MVHSGameEngineML import GameObject, PhysicsBody, AABBCollider, KeyInputType, Logger, Mode, Animator, ImageCache


class FlappyBatPlayer(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.starting_pos = pygame.Vector2(x, y)
        self.physics_body = PhysicsBody(self)
        self.physics_body.gravity_scale = 1.5
        self.physics_body.max_vel = config.PLAYER_MAX_VEL
        self.physics_body.collision_layer = config.LAYER_PLAYER
        self.physics_body.collision_mask = config.LAYER_BARRIER
        self.width = 30
        self.height = 30
        self.collider = AABBCollider(self, self.width, self.height, 0, 0)
        self.collider.draw_debug = config.DRAW_PHYSICS_DEBUG
        self.collider.receive_hit_events = True
        self.time_to_glide_animation = 0.12
        self.animator = Animator()


    def init(self):
        if self.world.mode == Mode.HUMAN_PLAY:

            input_manager = self.world.player_input_manager
            input_manager.register_key_input(KeyInputType.KEY_DOWN, pygame.K_SPACE, self.flap)

        if self.world.mode != Mode.AI_TRAIN_HEADLESS:
            self.animator = Animator()
            flap_animations = [
                # load_image("tile004.png", default_scale=2),
                ImageCache.load_image(config.IMAGES_DIR / "BatFlapFrame2.png", default_scale=2),
                ImageCache.load_image(config.IMAGES_DIR / "BatFlapFrame3.png", default_scale=2),
                ImageCache.load_image(config.IMAGES_DIR / "BatFlapFrame2.png", default_scale=2),
                ImageCache.load_image(config.IMAGES_DIR / "BatFlapFrame1.png", default_scale=2),
            ]
            self.animator.add_animation_state("flap", flap_animations, 0.09)

            glide_animations = [
                # load_image("tile004.png", default_scale=2),
                ImageCache.load_image(config.IMAGES_DIR / "BatFlapFrame1.png", default_scale=2),
            ]
            self.animator.add_animation_state("glide", glide_animations)
            self.animator.change_animation("glide")

    def flap(self):

        if self.world.game_over:
            return

        self.physics_body.add_force(pygame.Vector2(0, -1) * 80000)
        self.time_to_glide_animation = 0.3
        self.animator.change_animation("flap")


    def draw(self, renderer):
        if renderer is None:
            return

        #renderer.draw_rect_center(self.pos, pygame.Vector2(self.width, self.height), (66, 255, 0))
        if self.animator is not None:
            renderer.draw_image(self.animator.current_animation_frame, self.pos)


    def on_collision(self, other_game_object):
        self.physics_body.set_enabled(False)
        self.world.event_system.broadcast("on_player_collision")


    def update_frame(self, dt):
        super().update_frame(dt)

        if self.pos.y < -20 or self.pos.y > config.WINDOW_HEIGHT + 20:
            self.world.event_system.broadcast("on_player_collision")
            return

        if self.pos.x > self.world.total_world_length * 0.95:
            self.world.event_system.broadcast("on_player_won")
            self.physics_body.set_enabled(False)
            return

        if not self.world.game_over:
            self.animator.update(dt)
            self.physics_body.set_vel_x(380)
        self.time_to_glide_animation -= dt
        if self.time_to_glide_animation <= 0:
            self.animator.change_animation("glide")

    def apply_action(self, action):
        # Action == 0 for NOOP
        if action == 1:
            self.flap()


    def get_line_traces(self):

        physics_system = self.world.physics_system
        if physics_system is None:
            Logger.log_error(self, "Unable to find physics system")
            return None

        trace_ends = []
        start_degree = -90
        traces = config.PLAYER_NUM_TRACES
        trace_angle = config.PLAYER_TRACE_ANGLE
        for i in range(traces):
            rad = math.radians(start_degree)
            trace_end = self.pos + pygame.Vector2(math.cos(rad), math.sin(rad)) * 800
            trace_ends.append(trace_end)
            start_degree += trace_angle


        hit_distances = []
        for t in trace_ends:
            line_trace_result = physics_system.line_trace(self.pos, t, config.DRAW_PHYSICS_DEBUG, ignore=[self])
            if line_trace_result["hit_distance"] is not None:
                hit_distances.append(line_trace_result["hit_distance"])
            else:
                hit_distances.append(800)


        return hit_distances


    def restart(self):
        self.pos = self.starting_pos
        self.physics_body.set_enabled(True)
