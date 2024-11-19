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

    
    def accumulate_force(self, running_total, force_to_add):
        magnitude_so_far = running_total.length()
        magnitude_remaining = utils.MAX_STEERING_FORCE - magnitude_so_far

        if magnitude_remaining <= 0.0:
            return running_total

        magnitude_to_add = force_to_add.length()

        if magnitude_to_add < magnitude_remaining:
            running_total += force_to_add
        else:
            truncated_force = force_to_add.normalize() * magnitude_remaining
            running_total += truncated_force

        return running_total


    def calculate(self, obstacles, player):
        steering_force = pygame.Vector2(0, 0)
        is_close_to_player = self.agent.position.distance_to(player.position) <= utils.PANIC_DISTANCE
        if is_close_to_player:
            steering_force = self.hide(player, obstacles).normalize() * self.agent.max_speed
        # TODO combine other behaviors
        # avoid_force = self.obstacle_avoidance(obstacles).normalize() * self.agent.max_speed

        # combined_force = (
        #     flee_force * 0.5 +
        #     avoid_force * 1.0
        # )
        
        steering_force = pygame.Vector2.lerp(self.agent.velocity, steering_force, 0.1)
        return utils.truncate(steering_force, self.agent.max_speed)


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
    


    def wall_avoidance(self):
        detection_box_length = utils.MIN_DETECTION  + self.agent.velocity.magnitude() / self.agent.max_speed + utils.MAX_DETECTION
        feelers = [
            self.agent.position + self.agent.heading * detection_box_length,  # Center feeler
            self.agent.position + self.agent.heading.rotate(45) * detection_box_length * 0.5,  # Left feeler
            self.agent.position + self.agent.heading.rotate(-45) * detection_box_length * 0.5  # Right feeler
        ]

        for feeler in feelers:
            closest_intersection = None
            closest_dist = float('inf')
            pass


    def obstacle_avoidance(self, obstacles):
        detection_box_len = utils.MIN_DETECTION + (
            self.agent.velocity.magnitude() / self.agent.max_speed
        ) * (utils.MAX_DETECTION - utils.MIN_DETECTION)
        steering_force = pygame.Vector2(0,0)
        tagged_obstacles = self.agent.tag_neighbors(obstacles, detection_box_len)
    

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
        world_offset_pos = utils.point_to_world_space(
            offset,leader_agent.position, leader_agent.heading, leader_agent.side)
        to_offset = world_offset_pos - self.agent.position
        look_ahead_time = to_offset.length() / ( self.agent.max_speed + leader_agent.velocity.length() )
        return self.arrive(world_offset_pos + leader_agent.velocity.length() * look_ahead_time, Deceleration.FAST.value)


    def separation(self, neighbors):
        steering_force = pygame.Vector2(0, 0)
        for neighbor in neighbors:
            to_agent = self.agent.position - neighbor.position
            distance = to_agent.length()
            if distance > 0:
                steering_force += to_agent.normalize() / distance
        return steering_force
    

    def alignment(self, neighbors):
        if not neighbors:
            return pygame.Vector2(0, 0)
        avg_velocity = sum(neighbor.velocity for neighbor in neighbors) / len(neighbors)
        return (avg_velocity - self.agent.velocity).normalize()
    

    def cohesion(self, neighbors):
        if not neighbors:
            return pygame.Vector2(0, 0)



        center_of_mass = sum(neighbor.position for neighbor in neighbors) / len(neighbors)
        return (center_of_mass - self.agent.position).normalize()