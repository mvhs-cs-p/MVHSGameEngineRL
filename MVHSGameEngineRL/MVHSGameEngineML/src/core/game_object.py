import pygame



class GameObject:


    def __init__(self, x, y):
        self.name = ""
        self._pos = pygame.Vector2(x, y)
        self.world = None
        self.physics_body = None
        self.collider = None
        self.physics_system_id = -1
        self.surface = None
        self.animator = None
        self.width = 0
        self.height = 0


    def is_physics_object(self) -> bool:
        return (
                self.world is not None
                and self.physics_system_id >= 0 and
                self.world.physics_system is not None
        )


    @property
    def pos(self) -> pygame.Vector2:
        if self.is_physics_object():
            physics_system = self.world.physics_system
            i = self.physics_system_id
            return pygame.Vector2(physics_system.pos_x[i], physics_system.pos_y[i])
        else:
            return pygame.Vector2(self._pos.x, self._pos.y)

    @pos.setter
    def pos(self, value) -> None:
        if self.is_physics_object():
            physics_system = self.world.physics_system
            i = self.physics_system_id
            physics_system.pos_x[i] = float(value.x)
            physics_system.pos_y[i] = float(value.y)

        self._pos.x = float(value.x)
        self._pos.y = float(value.y)

    @property
    def vel(self) -> pygame.Vector2:
        if self.is_physics_object():
            physics_system = self.world.physics_system
            i = self.physics_system_id
            return pygame.Vector2(physics_system.vel_x[i], physics_system.vel_y[i])

        return pygame.Vector2(0, 0)


    def get_world(self):
        return self.world

    def get_physics_system(self):
        pass

    def init(self):
        pass

    def update_frame(self, dt):
        pass


    def draw(self, renderer):
        pass

    def restart(self):
        pass

    def on_hit(self, other_game_object):
        pass

    # def on_overlap(self, other_game_object):
    #     pass






