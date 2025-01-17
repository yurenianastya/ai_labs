import random
import pygame
import steering_behaviors as sb
import utils


class RavenBot:

    def __init__(self, spawn_node, graph):
        self.steering_behaviors = sb.SteeringBehavior(self)
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)
        self.velocity = pygame.Vector2(0, 0)
        self.max_speed = 100
        self.fov_angle = 60
        self.fov_range = 250  
        self.graph = graph
        self.path = []
        self.current_target = None
        self.current_node = spawn_node
        self.goals = utils.WANDER_NODES_IDX
        self.radius = 8
        self.react_radius = 20
        

    def update(self, dt, all_bots):
        self.update_movement(dt)
        self.check_fov(all_bots, [])


    def update_movement(self, dt):

        if not self.current_target and self.path:
            self.current_target = self.path.pop(0)

        if self.current_target:
            steering_force = self.steering_behaviors.calculate()
            self.velocity += steering_force 

            if self.velocity.length() > self.max_speed:
                self.velocity = self.velocity.normalize() * self.max_speed
            
            self.position += self.velocity * dt

            if self.position.distance_to(self.current_target.position) < self.react_radius:
                if self.path:
                    self.current_target = self.path.pop(0)
                else:
                    self.current_node = self.current_target
                    self.calculate_path()


    def calculate_path(self):
        goal_node = random.choice(self.goals)
        self.path = self.graph.a_star(self.current_node, goal_node)


    def check_fov(self, all_bots, nodes=[]):
        detected_bots = []
        detected_nodes = []
        forward_vector = self.velocity.normalize() if self.velocity.length() > 0 else pygame.Vector2(1, 0)

        for bot in all_bots:
            if bot != self:
                direction_to_bot = (bot.position - self.position).normalize()
                distance_to_bot = self.position.distance_to(bot.position)

                if distance_to_bot <= self.fov_range:
                    angle_to_bot = forward_vector.angle_to(direction_to_bot)
                    if abs(angle_to_bot) <= self.fov_angle / 2:
                        if not self.check_line_of_sight(self.position, bot.position):
                            detected_bots.append(bot)
                            

        for node in nodes:
            direction_to_node = (node.position - self.position).normalize()
            distance_to_node = self.position.distance_to(node.position)

            if distance_to_node <= self.fov_range:
                angle_to_node = forward_vector.angle_to(direction_to_node)
                if abs(angle_to_node) <= self.fov_angle / 2:
                    if not self.check_line_of_sight(self.position, node.position):
                        detected_nodes.append(node)
                        
        return detected_bots, detected_nodes
    

    def check_line_of_sight(self, start_position, end_position):
        direction = (end_position - start_position).normalize()
        max_distance = start_position.distance_to(end_position)
        intersection = utils.cast_ray(start_position, direction, max_distance)

        if intersection:
            return start_position.distance_to(intersection) < max_distance
        return False