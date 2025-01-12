import random
from pygame.math import Vector2


class SteeringBehavior:
    def __init__(self, bot):
        self.bot = bot

    def seek(self, target_position):
        desired_velocity = (target_position - self.bot.position).normalize() * self.bot.max_speed
        steering = desired_velocity - self.bot.velocity
        return steering

    def flee(self, target_position):
        desired_velocity = (self.bot.position - target_position).normalize() * self.bot.max_speed
        steering = desired_velocity - self.bot.velocity
        return steering

    def arrive(self, target_position, slowing_radius):
        to_target = target_position - self.bot.position
        distance = to_target.length()
        if distance < slowing_radius:
            desired_velocity = to_target.normalize() * self.bot.max_speed * (distance / slowing_radius)
        else:
            desired_velocity = to_target.normalize() * self.bot.max_speed
        steering = desired_velocity - self.bot.velocity
        return steering

    def wander(self, wander_radius, wander_distance, jitter):
        circle_center = self.bot.velocity.normalize() * wander_distance
        random_offset = Vector2(
            random.uniform(-1, 1) * jitter,
            random.uniform(-1, 1) * jitter
        ).normalize() * wander_radius
        target = self.bot.position + circle_center + random_offset
        return self.seek(target)

    def avoid(self, obstacles):
        for obstacle in obstacles:
            if self.bot.position.distance_to(obstacle.position) < self.bot.avoidance_radius:
                return self.flee(obstacle.position)
        return Vector2(0, 0)
