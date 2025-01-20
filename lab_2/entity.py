import random
import pygame
import behaviors as sb
import utils


class Agent:

    def __init__(self, spawn_node, graph, items):
        self.state = "random_walk"
        self.steering_behaviors = sb.SteeringBehavior(self)
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)
        self.velocity = pygame.Vector2(0, 0)
        self.max_speed = 75
        self.fov_angle = 60
        self.fov_range = 250
        self.graph = graph
        self.path = []
        self.current_target = None
        self.current_node = spawn_node
        self.items = items
        self.radius = 8
        self.react_radius = 15
        # agent's status
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.max_armor = 100
        self.last_armor_update = pygame.time.get_ticks() / 1000.0
        # shooting
        self.shooting_cooldown = 1.0
        self.time_since_last_shot = 0.0
        self.last_known_enemy_pos = None

    def update(self, dt, all_agents):
        if self.health <= 40 and self.armor <= 40:
            self.state = "seek_hp"
        elif self.last_known_enemy_pos:
            self.state = "seek_n_fight"
        else:
            self.state = "random_walk"
            
        self.time_since_last_shot += dt
        current_time = pygame.time.get_ticks() / 1000.0
        self.calculate_armor(current_time)
            
        enemies_in_fov = self.check_enemies_in_fov(all_agents)
        if enemies_in_fov and self.state != "seek_hp":
            self.check_and_shoot(enemies_in_fov, all_agents)
        else:
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
                if self.path:
                    self.current_target = self.path.pop(0)
                else:
                    self.current_node = self.current_target
                    self.calculate_path()
        else:
            self.calculate_path()


    def calculate_path(self):
        if self.state == "random_walk":
            goal_node = random.choice(list(self.graph.nodes.values()))
            self.path = self.graph.a_star(self.current_node.index, goal_node.index)
        elif self.state == "seek_hp":
            self.path = self.graph.path_to_closest_item(self.current_node, self.items)
        elif self.state == "seek_n_fight":
            goal_node = self.graph.get_node_by_position(self.last_known_enemy_pos)
            self.path = self.graph.a_star(self.current_node.index, goal_node.index)


    def check_and_shoot(self, detected_agents, all_agents):
        if detected_agents and self.time_since_last_shot >= self.shooting_cooldown:
            target_agent = detected_agents[0]
            self.shoot(target_agent, all_agents)

    def shoot(self, target_agent, all_agents):
        self.time_since_last_shot = 0.0
        utils.SHOTS.append((self.position, target_agent.position, 0.2))
        damage_to_armor = min(20, target_agent.armor)
        target_agent.armor -= damage_to_armor
        target_agent.health -= (20 - damage_to_armor)

        if target_agent.health <= 0:
            target_agent.health = 0
            utils.remove_agent(target_agent, all_agents)


    def check_enemies_in_fov(self, all_agents):
        detected_agents = []
        forward_vector = self.velocity.normalize() if self.velocity.length() > 0 else pygame.Vector2(1, 0)

        for agent in all_agents:
            if agent != self:
                direction_to_agent = (agent.position - self.position).normalize()
                distance_to_agent = self.position.distance_to(agent.position)

                if distance_to_agent <= self.fov_range:
                    angle_to_agent = forward_vector.angle_to(direction_to_agent)
                    if abs(angle_to_agent) <= self.fov_angle / 2:
                        if not self.check_line_of_sight(self.position, agent.position):
                            detected_agents.append(agent)

        return detected_agents

    def check_line_of_sight(self, start_position, end_position):
        direction = (end_position - start_position).normalize()
        max_distance = start_position.distance_to(end_position)
        intersection = utils.cast_ray(start_position, direction, max_distance)

        if intersection:
            return start_position.distance_to(intersection) < max_distance
        return False
    
    def pick_up_armor(self):
        self.armor = self.max_armor + 20
    
    def calculate_armor(self, current_time):
        if self.armor > 0 and current_time - self.last_armor_update >= 2:
            self.armor -= 20  
            if self.armor < 0:
                self.armor = 0
            self.last_armor_update = current_time
    

class PickupItem:

    def __init__(self, item_type, spawn_node, graph):
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)
        self.item_type = item_type
        self.node = spawn_node
        self.respawn_time = None
        self.graph = graph
    
    def respawn(self):
        new_node = random.choice(list(self.graph.nodes.values()))
        self.position = new_node.position
    
    @staticmethod
    def generate_items(graph):
        items = []
        used_nodes = set()  
        for i in range(5):
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

    