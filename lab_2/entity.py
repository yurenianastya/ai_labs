import random
import pygame
import behaviors
import utils


class Agent:

    def __init__(self, spawn_node, graph, items):
        self.fsm = behaviors.FSM(self)
        self.steering_behaviors = behaviors.SteeringBehavior(self)
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)
        self.velocity = pygame.Vector2(0, 0)
        self.max_speed = 80
        self.fov_angle = 60
        self.fov_range = 200
        self.graph = graph
        self.items = items
        self.path = []
        self.current_target = None
        self.current_node = spawn_node
        self.radius = 8
        self.react_radius = 20
        # agent's status
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.max_armor = 100
        self.last_armor_update = pygame.time.get_ticks() / 1000.0
        self.is_dead = False
        # shooting
        self.time_since_last_shot = 0.0
        self.target_enemy_node = None

    def update(self, dt, all_agents):
        self.time_since_last_shot += dt

        self.calculate_armor()
        self.calculate_health()

        self.fsm.update_state(all_agents)
        
        self.update_movement(dt)

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
                self.current_node = self.current_target
                if self.path:
                    self.current_target = self.path.pop(0)
                else:
                    self.calculate_path()

    def calculate_path(self):
        if self.fsm.state == "random_walk":
            goal_node = random.choice(list(self.graph.nodes.values()))
            self.path = self.graph.a_star(self.current_node.index, goal_node.index)
        elif self.fsm.state == "seek_item":
            self.path = self.graph.path_to_closest_item(self.current_node, self.items)
        elif self.fsm.state == "fight" or self.fsm.state == "pursuit":
            self.path = self.graph.a_star(self.current_node.index,
                                           self.target_enemy_node.index)

    def check_and_shoot(self, enemy_in_fov):
        if self.time_since_last_shot >= 1.0:
            self.shoot(enemy_in_fov)

    def shoot(self, target_agent):
        self.time_since_last_shot = 0.0
        utils.SHOTS.append((self.position, target_agent.position, 0.2))
        damage_to_armor = min(20, target_agent.armor)
        target_agent.armor -= damage_to_armor
        target_agent.health -= (20 - damage_to_armor)

    def get_first_enemy_in_fov(self, all_agents):
        forward_vector = self.velocity.normalize() if self.velocity.length() > 0 else pygame.Vector2(1, 0)
        for agent in all_agents:
            if agent != self:
                direction_to_agent = (agent.position - self.position).normalize()
                distance_to_agent = self.position.distance_to(agent.position)

                if distance_to_agent <= self.fov_range:
                    angle_to_agent = forward_vector.angle_to(direction_to_agent)
                    if abs(angle_to_agent) <= self.fov_angle / 2:
                        if not self.check_line_of_sight(self.position, agent.position):
                            return agent
        return None
    
    def get_closest_item(self):
        forward_vector = self.velocity.normalize() if self.velocity.length() > 0 else pygame.Vector2(1, 0)

        for item in self.items:
            direction_to_agent = (item.position - self.position).normalize()
            distance_to_agent = self.position.distance_to(item.position)

            if distance_to_agent <= self.fov_range:
                angle_to_agent = forward_vector.angle_to(direction_to_agent)
                if abs(angle_to_agent) <= self.fov_angle / 2:
                    if not self.check_line_of_sight(self.position, item.position):
                        return item
        return None

    def check_line_of_sight(self, start_position, end_position):
        direction = (end_position - start_position).normalize()
        max_distance = start_position.distance_to(end_position)
        intersection = utils.cast_ray(start_position, direction, max_distance)

        if intersection:
            return start_position.distance_to(intersection) < max_distance
        return False
    
    def pick_up_armor(self):
        self.armor = self.max_armor + 20
    
    def calculate_armor(self):
        current_time = pygame.time.get_ticks() / 1000.0
        if self.armor > 0 and current_time - self.last_armor_update >= 2:
            self.armor -= 20  
            if self.armor < 0:
                self.armor = 0
            self.last_armor_update = current_time

    def calculate_health(self):
        if self.health <= 0:
            self.is_dead = True

class PickupItem:

    def __init__(self, item_type, spawn_node, graph):
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)
        self.item_type = item_type
        self.node = spawn_node
        self.graph = graph
    
    def respawn(self):
        self.node = random.choice(list(self.graph.nodes.values()))
        self.position = self.node.position
    
    @staticmethod
    def generate_items(graph):
        items = []
        used_nodes = set()  
        for _ in range(5):
            health_node = random.choice(list(graph.nodes.values()))
            while health_node.index in used_nodes or utils.is_edge_node(health_node, graph) or utils.is_item_too_close(health_node, items):  
                health_node = random.choice(list(graph.nodes.values()))
            used_nodes.add(health_node.index)
            items.append(PickupItem("health", health_node, graph))
            armor_node = random.choice(list(graph.nodes.values()))
            while armor_node.index in used_nodes or utils.is_edge_node(armor_node, graph) or utils.is_item_too_close(armor_node, items):  
                armor_node = random.choice(list(graph.nodes.values()))
            used_nodes.add(armor_node.index)
            items.append(PickupItem("armor", armor_node, graph))
        return items

    