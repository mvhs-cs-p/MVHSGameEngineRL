import pygame

from MVHSGameEngineML.src.core import game_object
from MVHSGameEngineML.src.input.player_input_manager import PlayerInputManager
from MVHSGameEngineML.src.rendering.renderer import Renderer
from MVHSGameEngineML.src.rendering.ui.ui_overlay import UIOverlay
from MVHSGameEngineML.src.core.config import EngineConfig, Mode
from MVHSGameEngineML.src.physics.physics_system import PhysicsSystem
from MVHSGameEngineML.src.camera import Camera
from MVHSGameEngineML.src.utilities import EventSystem


class World:
    def __init__(self, mode):
        self.game_objects = []
        self.game_objects_to_remove = []
        self.physics_system = PhysicsSystem()
        self.event_system = EventSystem()

        self.physics_bodies = []
        self.colliders = []
        self.pygame_window = None
        self.player_input_manager = PlayerInputManager()
        self.renderer = None
        self.ui_overlay = None
        self.quit_pending = False
        self.mode = mode
        self.camera = None
        self.world_time = 0

        self.background_color = (0, 0, 0)
        self.world_backdrop = None
        self.window_size = None
        self.window_center = None

        self.game_name = "RL Game"




    def add_game_object(self, game_object):
        self._add_game_object_internal(game_object)

    def add_game_objects(self, *game_objects):
        for obj in game_objects:
            if isinstance(obj, list) or isinstance(obj, tuple):
                for inner in obj:
                    self._add_game_object_internal(inner)
            else:
                self._add_game_object_internal(obj)

    def _add_game_object_internal(self, game_object):
        if game_object not in self.game_objects:
            game_object.world = self

            # See physics system needs to know about this game object
            if game_object.physics_body is not None or game_object.collider is not None:
                self.physics_system.add_physics_game_object(game_object)


            game_object.init()
            self.game_objects.append(game_object)


        if game_object.physics_body is not None and game_object.physics_body not in self.physics_bodies:
            self.physics_bodies.append(game_object.physics_body)

        if game_object.collider is not None and game_object.collider not in self.colliders:
            self.colliders.append(game_object.collider)


    def remove_game_object(self, game_object):
        if game_object not in self.game_objects_to_remove:
            self.game_objects_to_remove.append(game_object)


    def _remove_game_object_internal(self, game_object):
        if game_object.physics_system_id >= 0:
            self.physics_system.remove(game_object.physics_system_id)

        if game_object.physics_body is not None and game_object.physics_body in self.physics_bodies:
            self.physics_bodies.remove(game_object.physics_body)

        if game_object.collider is not None and game_object.collider in self.colliders:
            self.colliders.remove(game_object.collider)

        if game_object in self.game_objects:
            self.game_objects.remove(game_object)

        game_object.world = None


    def add_physics_bodies(self, physics_bodies):
        if physics_bodies not in self.physics_bodies:
            self.physics_bodies.append(physics_bodies)


    def draw_world(self):
        if self.mode == Mode.AI_TRAIN_HEADLESS:
            return

        if self.world_backdrop is not None:
            self.renderer.draw_backdrop(self.world_backdrop)
        else:
            self.pygame_window.fill(self.background_color)

        for go in self.game_objects:

            # pygame has some culling already built in. Look at putting this back in only if needed
            # if not self.camera.cull_game_object(game_object):
            #     game_object.draw(self.renderer)

            go.draw(self.renderer)
            if go.collider is not None and go.collider.draw_debug == True:
                go.collider.draw()

        if self.camera is not None:
            saved_camera_pos = self.camera.pos.copy()
            self.camera.pos = pygame.Vector2(0, 0)
            self.ui_overlay.draw()
            self.camera.pos = saved_camera_pos

        self.physics_system.draw_debug_traces(self.renderer)


    def tick(self, dt):
        self.world_time += dt
        self.physics_system.step(dt)
        self.update_frame(dt)

        for game_object in self.game_objects_to_remove:
            self._remove_game_object_internal(game_object)
        self.game_objects_to_remove.clear()


    def physics_step(self, dt):
        for physics_body in self.physics_bodies:
            physics_body.step(dt)

    def update_frame(self, dt):
        for game_object in self.game_objects:
            game_object.update_frame(dt)

    def world_to_start(self):
        pass

    def render(self):
        pygame.event.pump()
        self.draw_world()
        pygame.display.flip()

    def create_world(self, width, height):
        pygame.init()

        if self.mode == Mode.HUMAN_PLAY:
            self.pygame_window = pygame.display.set_mode((width, height))
            self.window_size = self.pygame_window.get_size()
            self.window_center = self.window_size[0] // 2, self.window_size[1] // 2
            self.camera = Camera(width, height)
            pygame.display.set_caption(self.game_name)
            self.renderer = Renderer(self.pygame_window, self, self.camera)
            self.ui_overlay = UIOverlay(self.renderer)
        elif self.mode == Mode.AI_TRAIN or self.mode == Mode.AI_PLAY:
            self.pygame_window = pygame.display.set_mode((width, height))
            self.window_size = self.pygame_window.get_size()
            self.window_center = self.window_size[0] // 2, self.window_size[1] // 2
            self.camera = Camera(width, height)
            pygame.display.set_caption(self.game_name)
            self.renderer = Renderer(self.pygame_window, self, self.camera)
            self.ui_overlay = UIOverlay(self.renderer)
            #self.renderer = Renderer(self.pygame_window, self)
        elif self.mode == Mode.AI_TRAIN_HEADLESS:
            self.pygame_window = None
            self.renderer = None
            self.ui_overlay = None
            self.camera = None

        self.world_to_start()


    def start_world(self):
        self.run_world()

    def restart(self):

        self.world_time = 0

        for physics_body in self.physics_bodies:
            physics_body.reset()

        for game_object in self.game_objects:
            game_object.restart()


    def handle_inputs(self):
        pygame_events = pygame.event.get()

        for pygame_event in pygame_events:
            if pygame_event.type == pygame.QUIT:
                self.quit_pending = True
                return

        # Only send mouse down events to overlay

        if self.ui_overlay is not None:
            for pygame_event in pygame_events:
                if pygame_event.type == pygame.MOUSEBUTTONDOWN:
                    self.ui_overlay.process_input(pygame_event)

        if self.player_input_manager is not None:
            self.player_input_manager.process_input(pygame, pygame_events)


    def run_world(self):
        while True:

            delay_ms = int(1000 * EngineConfig.fixed_dt)
            pygame.time.delay(delay_ms)

            # Get Input
            self.handle_inputs()
            if self.quit_pending:
                return
            # self.player_input_manager.process_input(pygame)
            # if self.player_input_manager.wants_to_quit:
            #     return

            self.tick(EngineConfig.fixed_dt)
            self.render()



