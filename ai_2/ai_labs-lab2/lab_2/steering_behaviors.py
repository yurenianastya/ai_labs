import random
import pygame
import utils


class SteeringBehavior:

    def __init__(self, bot):
        self.bot = bot

    def calculate(self):

        total_force = pygame.Vector2(0, 0)
        avoid_force = self.avoid()
        total_force += avoid_force * 0.9


        if avoid_force.length() > 0.1:
            return total_force
        
        wander_force = self.wander()
        total_force += wander_force * 0.4
        # elif self.behavior == "seek" and self.target_position:
        #     seek_force = self.bot.steering_behaviors.seek(self.bot.target_position)
        #     total_force += seek_force

        return total_force

    def seek(self, target_position):
        desired_velocity = target_position - self.bot.position
        if desired_velocity.length() > 0:
            desired_velocity = desired_velocity.normalize() * self.bot.max_speed
            steering = desired_velocity - self.bot.velocity
            return steering
        else:
            return pygame.Vector2(0, 0)

    def flee(self, target_position):
        desired_velocity = self.bot.position - target_position
        if desired_velocity.length() > 0:
            desired_velocity = desired_velocity.normalize() * self.bot.max_speed
            steering = desired_velocity - self.bot.velocity
            return steering
        else:
            return pygame.Vector2(0, 0)

    def arrive(self, target_position, slowing_radius):
        to_target = target_position - self.bot.position
        distance = to_target.length()
        if distance < slowing_radius:
            desired_velocity = to_target.normalize() * self.bot.max_speed * (distance / slowing_radius)
        else:
            desired_velocity = to_target.normalize() * self.bot.max_speed
        steering = desired_velocity - self.bot.velocity
        return steering

    def wander(self):
        if not self.bot.goal or not self.bot.path:
            self.bot.goal = self.bot.graph.nodes.get(random.choice(utils.WANDER_NODES_IDX))
            self.bot.path = self.bot.graph.a_star(self.bot.node, self.bot.goal)

        if self.bot.path:
            next_node = self.bot.path[0]
            target_position = next_node.position
            steering_force = self.seek(target_position)

            if self.bot.position.distance_to(target_position) < 5:
                self.bot.path.pop(0)

            return steering_force
        
        return pygame.Vector2(0, 0)

    def avoid(self):
        for polygon in utils.POLYGONS:
            for i in range(len(polygon)):
                p1 = pygame.Vector2(polygon[i])
                p2 = pygame.Vector2(polygon[(i + 1) % len(polygon)])
                closest_point = utils.closest_point_on_segment(self.bot.position, p1, p2)
                distance = self.bot.position.distance_to(closest_point)
                if distance < self.bot.avoidance_radius:
                    return self.flee(closest_point)
        
        for rect in utils.RECTS:
            if rect.collidepoint(self.bot.position):
                closest_point = utils.closest_point_to_rect(self.bot.position, rect)
                return self.flee(closest_point)
        
        for wall in utils.WALLS:
            if wall.collidepoint(self.bot.position):
                closest_point = utils.closest_point_to_rect(self.bot.position, wall)
                return self.flee(closest_point)
            
        return pygame.Vector2(0, 0)
