import pygame
import random
import math
import utils
from enum import Enum


class Deceleration(Enum):
    SLOW = 5
    NORMAL = 3
    FAST = 1


class SteeringBehaviors():


    def __init__(self, agent):
        self.agent = agent


    def accumulate_force(running_total, force_to_add):
        magnitude_so_far = running_total.length()
        magnitude_remaining = utils.MAX_STEERING_FORCE - magnitude_so_far
        if magnitude_remaining <= 0.0: return False
        magnitude_to_add = force_to_add.length()
        if magnitude_to_add < magnitude_remaining:
            running_total += force_to_add
        else:
            running_total += force_to_add.normalize() * magnitude_remaining
        return True


    def calculate(self, obstacles, player, zombies):
        steering_force = pygame.Vector2(0, 0)

        w_avoidance = 0.95
        w_separation = 0.7
        w_cohesion = 0.2
        w_alignment = 0.35
        w_wander = 0.4
        w_hide = 0.4
        w_flee = 0.5
        w_pursuit = 0.4

        # state depends on how many friends and how close?
        zombie_neighbors = self.agent.tag_neighbors(zombies, utils.NEIGHBOR_RADIUS)
        is_close_to_target = self.agent.position.distance_squared_to(player.position) <= utils.PANIC_DISTANCE ** 2

        # general force for all states
        avoidance_force = self.obstacle_avoidance(obstacles) * w_avoidance
        if not SteeringBehaviors.accumulate_force(steering_force, avoidance_force): return steering_force
        separation_force = self.separation(zombie_neighbors) * w_separation
        if not SteeringBehaviors.accumulate_force(steering_force, separation_force): return steering_force

        # state - hide if danger amd small group
        if is_close_to_target and len(zombie_neighbors) < 5:
            self.agent.color = utils.COLORS['YELLOW']
            flee_force = self.flee(player.position) * w_flee
            if not SteeringBehaviors.accumulate_force(steering_force, flee_force): return steering_force
            # hide_force = self.hide(player, obstacles) * w_hide
            # if not SteeringBehaviors.accumulate_force(steering_force, hide_force): return steering_force
        
        # state - wander to find others if no danger
        if not is_close_to_target and len(zombie_neighbors) < 5:
            self.agent.color = utils.COLORS['BLUE']
            cohesion_force = self.cohesion(zombie_neighbors) * w_cohesion
            if not SteeringBehaviors.accumulate_force(steering_force, cohesion_force): return steering_force
            wander_force = self.wander(5, 2, 7) * w_wander
            if not SteeringBehaviors.accumulate_force(steering_force, wander_force): return steering_force
        # state - if big group then pursuit
        if len(zombie_neighbors) > 5:
            self.agent.color = utils.COLORS['RED']
            alignment_force = self.alignment(zombie_neighbors) * w_alignment
            if not SteeringBehaviors.accumulate_force(steering_force, alignment_force): return steering_force
            pursuit_force = self.pursuit(player) * w_pursuit
            if not SteeringBehaviors.accumulate_force(steering_force, pursuit_force): return steering_force
        return steering_force


    def seek(self, target_pos):
        desired_velocity = pygame.Vector2.normalize(target_pos - self.agent.position) * self.agent.max_speed
        return desired_velocity - self.agent.velocity
    

    def flee(self, target_pos):
        if self.agent.position.distance_squared_to(target_pos) > utils.PANIC_DISTANCE ** 2:
            return pygame.Vector2(0,0)
        desired_velocity = pygame.Vector2.normalize(self.agent.position - target_pos) * self.agent.max_speed
        return desired_velocity - self.agent.velocity
    

    def arrive(self, target_pos, deceleration):
        to_target = (target_pos - self.agent.position)
        distance = to_target.length()
        if distance > 0:
            deceleration_tweaker = 0.1
            speed = distance / (deceleration * deceleration_tweaker)
            speed = min(speed, self.agent.max_speed)
            desired_velocity = to_target * speed / distance
            return (desired_velocity - self.agent.velocity)
        return pygame.Vector2(0,0)
    

    def pursuit(self, evader):
        # check if evader is just ahead then seek straight otherwise pursuit
        dist_to_evader = evader.position - self.agent.position
        relative_heading = self.agent.heading.dot(evader.heading)
        if dist_to_evader.dot(self.agent.heading) > 0 and relative_heading < -0.95:
            return self.seek(evader.position)
        look_ahead_time = dist_to_evader.length() / self.agent.max_speed + evader.velocity.length()
        return self.seek(evader.position + evader.velocity * look_ahead_time)
    

    def evade(self, pursuer):
        dist_to_pursuer = pursuer.position - self.agent.position
        look_ahead_time = dist_to_pursuer.length() / self.agent.max_speed + pursuer.velocity.length()
        return self.flee(pursuer.position + pursuer.velocity * look_ahead_time)
    

    def wander(self, wander_distance, wander_jitter, wander_radius):
        self.agent.wander_target += pygame.Vector2(
            random.uniform(-1, 1) * wander_jitter,
            random.uniform(-1, 1) * wander_jitter
            )
        self.agent.wander_target = self.agent.wander_target.normalize() * wander_radius
        target_local = self.agent.wander_target + pygame.Vector2(wander_distance, 0)

        current_direction = self.agent.velocity.normalize()
        
        desired_direction = target_local.normalize()

        angle_to_target = math.atan2(desired_direction.y, desired_direction.x) - math.atan2(current_direction.y, current_direction.x)
        angle_to_target = (angle_to_target + math.pi) % (2 * math.pi) - math.pi
        clamped_angle = max(-self.agent.max_turn_rate, min(self.agent.max_turn_rate, angle_to_target))

        cos_angle = math.cos(clamped_angle)
        sin_angle = math.sin(clamped_angle)
        rotated_direction = pygame.Vector2(
            current_direction.x * cos_angle - current_direction.y * sin_angle,
            current_direction.x * sin_angle + current_direction.y * cos_angle
            )

        self.agent.velocity = rotated_direction * self.agent.max_speed
        
        target_world = self.agent.position + self.agent.velocity
        return target_world - self.agent.position
    

    def obstacle_avoidance(self, obstacles):
        detection_box_len = utils.MIN_DETECTION_LEN + (
            self.agent.velocity.magnitude() / self.agent.max_speed
        ) * utils.MIN_DETECTION_LEN
        tagged_obstacles = self.agent.tag_neighbors(obstacles, detection_box_len)
        closest_intersect_obstacle = None
        dist_closest_ip = math.inf
        local_pos_of_closest = pygame.Vector2(0,0)

        for obstacle in tagged_obstacles:
            local_pos = SteeringBehaviors.point_to_local_space(
                obstacle.position,
                self.agent.heading,
                self.agent.side,
                self.agent.position,
            )
            if local_pos.x > 0:
                expanded_radius = obstacle.radius + self.agent.radius
                if math.fabs(local_pos.y) < expanded_radius:
                    c_x = local_pos.x
                    c_y = local_pos.y
                    sqrt_part = math.sqrt(max(0, expanded_radius**2 - c_y**2))
                    ip = c_x - sqrt_part
                    if ip <= 0:
                        ip = c_x + sqrt_part
                    if ip < dist_closest_ip:
                        dist_closest_ip = ip
                        closest_intersect_obstacle = obstacle
                        local_pos_of_closest = local_pos

        avoidance_force = pygame.Vector2(0,0)
        if closest_intersect_obstacle:
            multiplier = 1.0 + (detection_box_len - local_pos_of_closest.x) / detection_box_len
            avoidance_force.y = (closest_intersect_obstacle.radius - local_pos_of_closest.y) * multiplier
            braking_weight = 0.4
            avoidance_force.x = (closest_intersect_obstacle.radius - local_pos_of_closest.x) * braking_weight
        return SteeringBehaviors.vector_to_world_space(
            avoidance_force,
            self.agent.heading,
            self.agent.side,
        )


    def create_feelers(self):
        # point in front
        self.agent.feelers[0] = self.agent.position + utils.WALL_DETECTION_LEN * self.agent.heading
        # to left
        temp = self.agent.heading
        temp.rotate(math.pi / 2 * 3.5)
        self.agent.feelers[1] = self.agent.position + utils.WALL_DETECTION_LEN / 2.0 * temp
        # to right
        temp = self.agent.heading
        temp.rotate(math.pi / 2 * 0.5)
        self.agent.feelers[2] = self.agent.position + utils.WALL_DETECTION_LEN / 2.0 * temp
        

    
    def interpose(self, agent_a, agent_b):
        mid_point = (agent_a.position + agent_b.position) / 2.0
        time_to_mid_point = pygame.Vector2.distance_to(self.agent.position, mid_point) / self.agent.max_speed
        A_pos = agent_a.position + agent_a.velocity * time_to_mid_point
        B_pos = agent_b.position + agent_b.velocity * time_to_mid_point
        mid_point = (A_pos + B_pos) / 2.0
        return self.arrive(mid_point, Deceleration.FAST.value) 
    

    def get_hiding_position(obstacle_pos, obstacle_r, target_pos):
        dist_from_boundary = 30.0
        distance_away = obstacle_r + dist_from_boundary
        vec_to_obstacle = pygame.Vector2.normalize(obstacle_pos - target_pos)
        return (vec_to_obstacle * distance_away) + obstacle_pos
    

    def hide(self, target, obstacles):
        dist_to_closest = float('inf')
        best_hiding_spot = None
        for obstacle in obstacles:
            hiding_spot = SteeringBehaviors.get_hiding_position(obstacle.position, obstacle.radius, target.position)
            distance = pygame.Vector2.distance_squared_to(hiding_spot, self.agent.position)
            if distance < dist_to_closest:
                dist_to_closest = distance
                best_hiding_spot = hiding_spot
        if (dist_to_closest == float('inf')):
            return self.evade(target)
        return self.arrive(best_hiding_spot, Deceleration.FAST.value)
    

    def offset_pursuit(self, leader_agent, offset):
        world_offset_pos = SteeringBehaviors.point_to_world_space(
            offset,leader_agent.position, leader_agent.heading, leader_agent.side)
        to_offset = world_offset_pos - self.agent.position
        look_ahead_time = to_offset.length() / ( self.agent.max_speed + leader_agent.velocity.length() )
        return self.arrive(world_offset_pos + leader_agent.velocity.length() * look_ahead_time, Deceleration.FAST.value)


    def separation(self, zombie_neighbors):
        steering_force = pygame.Vector2(0, 0)
        for neighbor in zombie_neighbors:
            to_agent = self.agent.position - neighbor.position
            distance = to_agent.length()
            if distance > 0:
                steering_force += to_agent.normalize() / distance
        return steering_force
    

    def alignment(self, neighbors):
        if not neighbors:
            return pygame.Vector2(0, 0)
        avg_velocity = sum((neighbor.velocity for neighbor in neighbors), pygame.Vector2(0,0)) / len(neighbors)
        return (avg_velocity - self.agent.velocity).normalize()
    

    def cohesion(self, neighbors):
        if not neighbors:
            return pygame.Vector2(0, 0)
        center_of_mass = sum((neighbor.velocity for neighbor in neighbors), pygame.Vector2(0,0)) / len(neighbors)
        return (center_of_mass - self.agent.position).normalize()
    
       
    def point_to_world_space(point, agent_position, heading, side):
        world_x = point.x * heading.x + point.y * side.x
        world_y = point.x * heading.y + point.y * side.y
        rotated_point = pygame.Vector2(world_x, world_y)
        world_point = rotated_point + agent_position
        return world_point
    

    def point_to_local_space(point, heading, side, agent_position):
        translated_point = point - agent_position
        local_x = translated_point.dot(heading)
        local_y = translated_point.dot(side)
        return pygame.Vector2(local_x, local_y)
    

    def world_to_local_space(agent, world_position):
        heading = agent.velocity.normalize()
        side = pygame.Vector2(-heading.y, heading.x)
        local_x = heading.dot(world_position - agent.position)
        local_y = side.dot(world_position - agent.position)
        return pygame.Vector2(local_x, local_y)
    

    def local_to_world_space(agent, local_vector):
        heading = agent.velocity.normalize()
        side = pygame.Vector2(-heading.y, heading.x)
        world_x = heading.x * local_vector.x + side.x * local_vector.y
        world_y = heading.y * local_vector.x + side.y * local_vector.y
        return pygame.Vector2(world_x, world_y)
    

    def vector_to_world_space(vec, agent_heading, agent_side):
        transform_matrix = [
            [agent_heading.x, agent_side.x],
            [agent_heading.y, agent_side.y]
        ]
        world_x = vec.x * transform_matrix[0][0] + vec.y * transform_matrix[0][1]
        world_y = vec.x * transform_matrix[1][0] + vec.y * transform_matrix[1][1]
        return pygame.Vector2(world_x, world_y)
    

    def is_zero(vec):
        return math.isclose(vec.magnitude(), 0)
