import pygame


class PhysicsBody:
    def __init__(self, owner):
        self.owner = owner
        self._vel = pygame.Vector2(0, 0)
        self.max_vel = float('inf')
        self.added_forces = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.gravity_scale = 1
        self.mass = 1.0
        self.drag_k = 1.0
        self.friction = 1.0
        self.enabled = True
        self.is_static = False
        self.collision_layer = 0
        self.collision_mask = 0

    def get_physics_system(self):

        if self.owner is not None:
            return self.owner.world.physics_system

        return None

    def reset(self) -> None:

        """
        Reset physics body, set velocity and acceleration to 0 and remove all pending added forces.
        """
        physics_system = self.get_physics_system()
        if physics_system is not None:
            physics_system.reset_physics_body(self.owner.physics_system_id)


    def set_enabled(self, enabled: bool) -> None:

        physics_system = self.get_physics_system()
        if physics_system is not None:
            physics_system.set_enabled(self.owner.physics_system_id, enabled)


    def set_drag_k(self, drag_k: float) -> None:

        physics_system = self.get_physics_system()
        if physics_system is not None:
            physics_system.set_drag_k(self.owner.physics_system_id, drag_k)


    def set_max_vel_mag(self, max_vel: float) -> None:
        physics_system = self.get_physics_system()
        if physics_system is not None:
            physics_system.set_max_vel_mag(self.owner.physics_system_id, max_vel)


    def add_force(self, force: pygame.Vector2) -> None:

        """
        Add force to physics body. Added forces and used during next physics step. All added forces
        are cleared at the end of each physics step.
        :return:
        """
        physics_system = self.get_physics_system()
        if physics_system is not None:
            physics_system.apply_added_force(self.owner.physics_system_id, force)

    def reset_physics_body(self) -> None:
        physics_system = self.get_physics_system()
        if physics_system is not None:
            physics_system.reset_physics_body(self.owner.physics_system_id)


    def clear_added_forces(self) -> None:

        """
        Clear added forces from this physics body. Does not change current velocity.
        """

        physics_system = self.get_physics_system()
        if physics_system is not None:
            physics_system.clear_added_forces(self.owner.physics_system_id)

    @property
    def vel(self) -> pygame.Vector2:
        physics_system = self.get_physics_system()
        physics_system_id = self.owner.physics_system_id
        return pygame.Vector2(physics_system.vel_x[physics_system_id], physics_system.vel_y[physics_system_id])


    @vel.setter
    def vel(self, value:pygame) -> None:
        physics_system = self.get_physics_system()
        physics_system_id = self.owner.physics_system_id
        physics_system.vel_x[physics_system_id] = value.x
        physics_system.vel_y[physics_system_id] = value.y


    def set_vel_x(self, x:float) -> None:
        physics_system = self.get_physics_system()
        physics_system_id = self.owner.physics_system_id
        physics_system.vel_x[physics_system_id] = x


    def set_vel_y(self, y: float) -> None:
        physics_system = self.get_physics_system()
        physics_system_id = self.owner.physics_system_id
        physics_system.vel_x[physics_system_id] = y


