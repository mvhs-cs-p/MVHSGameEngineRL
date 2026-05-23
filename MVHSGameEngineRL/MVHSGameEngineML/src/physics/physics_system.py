import math

import pygame
from pygame import Vector2

from ..collision.collision_resolver import CollisionResolver
from ..utilities.logger import Logger



class PhysicsSystem:

    default_size = 256

    def __init__(self) -> None:
        self.owners = [None] * PhysicsSystem.default_size
        self.pos_x = [0.0] * PhysicsSystem.default_size
        self.pos_y = [0.0] * PhysicsSystem.default_size
        self.vel_x = [0.0] * PhysicsSystem.default_size
        self.vel_y = [0.0] * PhysicsSystem.default_size
        self.mass = [0.0] * PhysicsSystem.default_size
        self.gravity_scale = [0.0] * PhysicsSystem.default_size
        self.added_forces_x = [0.0] * PhysicsSystem.default_size
        self.added_forces_y = [0.0] * PhysicsSystem.default_size
        self.acceleration_x = [0.0] * PhysicsSystem.default_size
        self.acceleration_y = [0.0] * PhysicsSystem.default_size
        self.friction_x = [0.0] * PhysicsSystem.default_size
        self.friction_y = [0.0] * PhysicsSystem.default_size
        self.drag_k = [0.0] * PhysicsSystem.default_size
        self.max_speed = [0.0] * PhysicsSystem.default_size
        self.has_collider = [False] * PhysicsSystem.default_size
        #self.receive_overlap_event = [False] * PhysicsSystem.default_size
        self.receive_collision_event = [False] * PhysicsSystem.default_size
        self.collider_size_x = [0] * PhysicsSystem.default_size
        self.collider_size_y = [0] * PhysicsSystem.default_size
        self.collider_offset_x = [0.0] * PhysicsSystem.default_size
        self.collider_offset_y = [0.0] * PhysicsSystem.default_size
        self.enabled = [False] * PhysicsSystem.default_size
        self.is_static = [False] * PhysicsSystem.default_size
        self.is_active = [False] * PhysicsSystem.default_size
        self.collision_layer = [0] * PhysicsSystem.default_size
        self.collision_mask = [0] * PhysicsSystem.default_size

        self.max_set_index = 0

        self.debug = False
        self.debug_trace_results = []


    def add_physics_game_object(self, game_object):

        if game_object.physics_body is None and game_object.AABBCollider is None:
            Logger.log_warning(self, "Trying to add physics game object without physics body or AABB collider")
            return

        index = self.get_next_available_index()
        self.owners[index] = game_object
        self.is_active[index] = True

        game_object.physics_system_id = index
        self.is_static[index] = game_object.physics_body.is_static
        self.enabled[index] = game_object.physics_body.enabled

        # Must use protected pos. Otherwise will read value from pos arrays when accessing pos property in gameobject
        self.pos_x[index] = game_object._pos.x
        self.pos_y[index] = game_object._pos.y

        if game_object.physics_body is not None:
            self.vel_x[index] = game_object.physics_body._vel.x
            self.vel_y[index] = game_object.physics_body._vel.y
            self.mass[index] = game_object.physics_body.mass
            self.gravity_scale[index] = game_object.physics_body.gravity_scale
            self.max_speed[index] = game_object.physics_body.max_vel
            self.added_forces_x[index] = game_object.physics_body.added_forces.x
            self.added_forces_y[index] = game_object.physics_body.added_forces.y
            self.drag_k[index] = game_object.physics_body.drag_k
            self.friction_x[index] = game_object.physics_body.friction
            self.friction_y[index] = game_object.physics_body.friction
            self.collision_layer[index] = game_object.physics_body.collision_layer
            self.collision_mask[index] = game_object.physics_body.collision_mask

        if game_object.collider is not None:
            self.has_collider[index] = True
            self.collider_size_x[index] = game_object.collider.size.x
            self.collider_size_y[index] = game_object.collider.size.y
            self.collider_offset_x[index] = game_object.collider.offset.x
            self.collider_offset_y[index] = game_object.collider.offset.y
            #self.receive_overlap_event[index] = game_object.collider.receive_overlap_event
            self.receive_collision_event[index] = game_object.collider.receive_hit_events




    def get_next_available_index(self):
        for i in range(PhysicsSystem.default_size):
            if not self.is_active[i]:
                self.max_set_index = max(i, self.max_set_index)
                return i

        Logger.log_error(self, "PhysicsSystem.get_next_available_index(): max size exceeded")
        return None

    def remove(self, game_object_index):
        self.is_active[game_object_index] = False


    def reset_physics_body(self, game_object_index):
        self.vel_x[game_object_index] = 0.0
        self.vel_y[game_object_index] = 0.0
        self.acceleration_x[game_object_index] = 0.0
        self.acceleration_y[game_object_index] = 0.0
        self.added_forces_x[game_object_index] = 0.0
        self.added_forces_y[game_object_index] = 0.0


    def set_drag_k(self, game_object_index, drag_k: float) -> None:
        self.drag_k[game_object_index] = drag_k


    def set_max_vel_mag(self, game_object_index, vel: float) -> None:
        self.max_speed[game_object_index] = vel

    def apply_added_force(self, game_object_index, added_force):

        self.added_forces_x[game_object_index] += added_force.x
        self.added_forces_y[game_object_index] += added_force.y


    def set_enabled(self, game_object_index, enabled):
        self.enabled[game_object_index] = enabled


    def clear_added_force(self, game_object_index):
        self.added_forces_x[game_object_index] = 0.0
        self.added_forces_y[game_object_index] = 0.0


    def clamp_velocity(self, game_object_index):

        if self.max_speed[game_object_index] == float('inf'):
            return

        vel_vector = pygame.Vector2(self.vel_x[game_object_index], self.vel_y[game_object_index])
        if vel_vector.magnitude_squared() > self.max_speed[game_object_index]**2:
            vel_vector = vel_vector.normalize()
            self.vel_x[game_object_index] = vel_vector.x * self.max_speed[game_object_index]
            self.vel_y[game_object_index] = vel_vector.y * self.max_speed[game_object_index]


    def step(self, dt):

        for i in range(self.max_set_index + 1):

            if not self.is_active[i] or not self.enabled[i] or self.is_static[i]:
                continue

            drag_x = self.drag_k[i]
            drag_y = self.drag_k[i]

            # Need grounded check
            # if math.fabs(self.added_forces_x[i]) < 0.01 and math.fabs(self.added_forces_y[i]) < 0.01:
            #     drag_x = self.friction_x[i]
            #     drag_y = self.friction_y[i]

            self.added_forces_x[i] += self.vel_x[i] * - drag_x
            self.added_forces_y[i] += self.vel_y[i] * - drag_y
            self.acceleration_x[i] = self.added_forces_x[i] / self.mass[i] if self.mass[i] > 0 else 0
            self.acceleration_y[i] = self.added_forces_y[i] / self.mass[i] if self.mass[i] > 0 else 0

            if self.gravity_scale[i] > 0:
                self.acceleration_y[i] += self.gravity_scale[i] * 980.0

            self.vel_x[i] += self.acceleration_x[i] * dt
            self.clamp_velocity(i)
            self.pos_x[i] += self.vel_x[i] * dt
            CollisionResolver.resolve_axis(self, i, "X")

            self.vel_y[i] += self.acceleration_y[i] * dt
            self.clamp_velocity(i)
            self.pos_y[i] += self.vel_y[i] * dt
            CollisionResolver.resolve_axis(self, i, "Y")

            self.clear_added_force(i)

            owner = self.owners[i]
            if owner is not None:
                owner.pos.x = self.pos_x[i]
                owner.pos.y = self.pos_y[i]


    def get_collision_rect(self, game_object_index):

        """
        Get a pygame.Rect using the data stored in the SOA for a given index
        :param game_object_index:
        :return:
        """

        if game_object_index > self.max_set_index:
            return None
        if not self.has_collider[game_object_index]:
            return None

        collider_center_x = self.pos_x[game_object_index] + self.collider_offset_x[game_object_index]
        collider_center_y = self.pos_y[game_object_index] + self.collider_offset_y[game_object_index]
        half_width = self.collider_size_x[game_object_index] * 0.5
        half_height = self.collider_size_y[game_object_index] * 0.5
        left = collider_center_x - half_width
        top = collider_center_y - half_height
        return pygame.Rect(left, top, self.collider_size_x[game_object_index], self.collider_size_y[game_object_index])


    def line_trace(self, start_pos: pygame.Vector2|tuple[int, int], end_pos: pygame.Vector2|tuple[int, int], draw_debug = False, ignore=None):

        # Get all possible collision indices
        check_indices = []
        for i in range(self.max_set_index + 1):
            if not self.is_active[i] or not self.enabled[i] or not self.has_collider[i]:
                continue
            if ignore is not None and self.owners[i] in ignore:
                continue
            check_indices.append(i)

        # Keep track of the closest thing
        closest_object = None
        closest_point = None
        closest_distance = float('inf')

        for index in check_indices:

            collider_rect = self.get_collision_rect(index)
            clipped = collider_rect.clipline(start_pos, end_pos)

            if clipped:
                (x1, y1), (x2, y2) = clipped

                hit_point_1 = pygame.Vector2(x1, y1)
                hit_point_2 = pygame.Vector2(x2, y2)

                distance_1 = (hit_point_1 - start_pos).length_squared()
                distance_2 = (hit_point_2 - start_pos).length_squared()

                distance = distance_1 if distance_1 < distance_2 else distance_2
                if distance < closest_distance:
                    closest_distance = distance
                    closest_point = hit_point_1 if distance_1 < distance_2 else hit_point_2
                    closest_object = self.owners[index]

        if closest_object is not None:
            hit_result = {
                "hit_point": closest_point,
                "hit_distance": math.sqrt(closest_distance),
                "hit_game_object" : closest_object,
            }
            if self.debug and draw_debug:
                line_trace_debug_result = {
                    "hit_point": closest_point,
                    "start_pos": start_pos,
                    "end_pos": closest_point
                }
                self.debug_trace_results.append(line_trace_debug_result)
            return hit_result
        else:
            hit_result = {
                "hit_point": None,
                "hit_distance": None,
                "hit_game_object": None,
            }
            if self.debug and draw_debug:
                line_trace_debug_result = {
                    "hit_point": None,
                    "start_pos": start_pos,
                    "end_pos": end_pos
                }
                self.debug_trace_results.append(line_trace_debug_result)
            return hit_result


    def ray_trace(self, start_pos: pygame.Vector2, direction: pygame.Vector2, distance = 1000, draw_debug = False, ignore=None):
        end = start_pos + direction.normalize() * distance
        return self.line_trace(start_pos, end, draw_debug=draw_debug, ignore=ignore)


    def draw_debug_traces(self, renderer):

        """
        Draw debug lines from line and ray traces
        """

        if not self.debug:
            return

        for debug_trace in self.debug_trace_results:
            start = debug_trace['start_pos']
            end = debug_trace['hit_point'] if debug_trace['hit_point'] is not None else debug_trace['end_pos']
            renderer.draw_line(start, end, (0, 255, 0))

            hit_point = debug_trace['hit_point']
            if hit_point is not None:
                renderer.draw_ellipse_centered(hit_point, pygame.Vector2(10, 10), (255, 0, 0))

        self.debug_trace_results.clear()

