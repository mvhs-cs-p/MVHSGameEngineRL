import pygame


class CollisionResolver:

    @staticmethod
    def resolve_axis(physics_system, mover_id, axis):

        mover_center_x = physics_system.pos_x[mover_id] + physics_system.collider_offset_x[mover_id]
        mover_center_y = physics_system.pos_y[mover_id] + physics_system.collider_offset_y[mover_id]
        half_width = physics_system.collider_size_x[mover_id] * 0.5
        half_height = physics_system.collider_size_y[mover_id] * 0.5
        mover_left = mover_center_x - half_width
        mover_right = mover_center_x + half_width
        mover_top = mover_center_y - half_height
        mover_bottom = mover_center_y + half_height


        for other_id in range(physics_system.max_set_index + 1):

            if not (physics_system.collision_layer[other_id] & physics_system.collision_mask[mover_id] or
                    physics_system.collision_layer[mover_id] & physics_system.collision_mask[other_id]):
                continue



            if other_id == mover_id or not physics_system.is_active[other_id] or not physics_system.enabled[other_id] or not physics_system.has_collider[other_id]:
                continue

            other_center_x = physics_system.pos_x[other_id] + physics_system.collider_offset_x[other_id]
            other_center_y = physics_system.pos_y[other_id] + physics_system.collider_offset_y[other_id]
            half_width = physics_system.collider_size_x[other_id] * 0.5
            half_height = physics_system.collider_size_y[other_id] * 0.5
            other_left = other_center_x - half_width
            other_right = other_center_x + half_width
            other_top = other_center_y - half_height
            other_bottom = other_center_y + half_height

            # AABB overlap test
            if (mover_right <= other_left) or (mover_left >= other_right) or (mover_bottom <= other_top) or (mover_top >= other_bottom):
                continue

            collision_resolved = False

            # Collision
            if axis == "X":
                vel_x = physics_system.vel_x[mover_id]
                if vel_x > 0:
                    dx = other_left - mover_right
                    physics_system.pos_x[mover_id] += dx
                    collision_resolved = True
                elif vel_x < 0:
                    dx = other_right - mover_left
                    physics_system.pos_x[mover_id] += dx
                    collision_resolved = True
                physics_system.vel_x[mover_id] = 0

                mover_center_x = physics_system.pos_x[mover_id] + physics_system.collider_offset_x[mover_id]
                mover_center_y = physics_system.pos_y[mover_id] + physics_system.collider_offset_y[mover_id]
                half_width = physics_system.collider_size_x[mover_id] * 0.5
                half_height = physics_system.collider_size_y[mover_id] * 0.5
                mover_left = mover_center_x - half_width
                mover_right = mover_center_x + half_width
                mover_top = mover_center_y - half_height
                mover_bottom = mover_center_y + half_height

            elif axis == "Y":
                vel_y = physics_system.vel_y[mover_id]
                if vel_y > 0:
                    dy = other_top - mover_bottom
                    physics_system.pos_y[mover_id] += dy
                    collision_resolved = True
                elif vel_y < 0:
                    dy = other_bottom - mover_top
                    physics_system.pos_y[mover_id] += dy
                    collision_resolved = True
                physics_system.vel_y[mover_id] = 0


                mover_center_x = physics_system.pos_x[mover_id] + physics_system.collider_offset_x[mover_id]
                mover_center_y = physics_system.pos_y[mover_id] + physics_system.collider_offset_y[mover_id]
                half_width = physics_system.collider_size_x[mover_id] * 0.5
                half_height = physics_system.collider_size_y[mover_id] * 0.5
                mover_left = mover_center_x - half_width
                mover_right = mover_center_x + half_width
                mover_top = mover_center_y - half_height
                mover_bottom = mover_center_y + half_height

            if collision_resolved:
                if physics_system.receive_collision_event[mover_id]:
                    physics_system.owners[mover_id].on_collision(physics_system.owners[other_id])
                if physics_system.receive_collision_event[other_id]:
                    physics_system.owners[other_id].on_collision(physics_system.owners[mover_id])










