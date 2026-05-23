import pygame

from ..core.config import Mode, EngineConfig


class RLEnvironment:
    def __init__(self, world, mode):
        self.mode = mode
        self.world = world
        self.step_count = 0

        # Set by game config file in child classes
        self.max_steps = 0

    def restart(self):
        pass


    def get_observation(self):
        pass


    def get_observation_tensor(self):
        pass


    def step(self, action):
        pass


    def render(self):
        if self.mode == Mode.AI_TRAIN or self.mode == Mode.AI_PLAY:
            self.world.render()
            pygame.display.flip()
            delay_ms = int(1000 * EngineConfig.fixed_dt)
            pygame.time.wait(delay_ms)