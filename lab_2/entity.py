import random
import pygame
import behaviors as sb
import utils


class Agent:

    def __init__(self, spawn_node, graph, wander_nodes, items):
        self.state = "seek_enemies"
        self.steering_behaviors = sb.SteeringBehavior(self)
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)
        self.velocity = pygame.Vector2(0, 0)
        self.forward_vector = pygame.Vector2(1, 0)
        self.vision_vector = self.forward_vector.copy()
        self.max_speed = 75
        self.fov_angle = 30
        self.fov_range = 500
        self.graph = graph
        self.path = []
        self.current_target = None
        self.current_node = spawn_node
        self.wander_nodes = wander_nodes
        self.items = items
        self.radius = 8
        self.react_radius = 20
        # agent's status
        self.health = 100
        self.max_health = 100
        self.prev_health = 100
        self.armor = 0
        self.max_armor = 100
        self.last_armor_update = pygame.time.get_ticks() / 1000.0
        # shooting
        self.shooting_cooldown = 1.0
        self.time_since_last_shot = 0.0
        

    def update(self, dt, all_agents):

        if self.velocity.length() > 0:
            self.forward_vector = self.velocity.normalize()
            if self.vision_vector.length() == 0:
                self.vision_vector = self.forward_vector.copy()

        if self.health <= 40 and self.armor == 0:
            self.state = "seek_hp"
        else:
            self.state = "seek_enemies"
            
        self.time_since_last_shot += dt
        current_time = pygame.time.get_ticks() / 1000.0
        self.calculate_armor(current_time)
            
        enemies_in_fov = self.check_enemies_in_fov(all_agents)
        if enemies_in_fov and self.state == "seek_enemies":
            self.velocity = pygame.Vector2(0, 0)
            self.check_and_shoot(enemies_in_fov, all_agents)
        else:
            self.update_movement(dt)

        if self.health < self.prev_health:
            attacker = self.identify_attacker(all_agents)
            if attacker:
                self.rotate_vision(attacker)
                enemies_in_fov = self.check_enemies_in_fov(all_agents)
                if enemies_in_fov:
                    self.check_and_shoot(enemies_in_fov, all_agents)
        self.vision_vector = self.forward_vector.copy()

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
        if self.state == "seek_enemies":
            goal_node = random.choice(self.wander_nodes)
            self.path = self.graph.a_star(self.current_node.index, goal_node)
        elif self.state == "seek_hp":
            self.path = self.graph.path_to_closest_item(self.current_node, self.items)

    def detect_items(self):
        for item in self.items:
            if self.position.distance_to(item.position) < self.fov_range:
                if item.item_type == "armor" and self.armor < self.max_armor:
                    self.current_target = item.node
                    return True
                elif item.item_type == "health" and self.health < self.max_health:
                    self.current_target = item.node
                    return True
        return False

    def check_and_shoot(self, detected_agents, all_agents):
        if detected_agents and self.time_since_last_shot >= self.shooting_cooldown:
            target_agent = detected_agents[0]
            self.shoot(target_agent, all_agents)


    def shoot(self, target_agent, all_agents):
        self.time_since_last_shot = 0.0
        utils.SHOTS.append((self.position, target_agent.position, 0.2))
    
        if target_agent.armor > 0:
            damage_to_armor = min(20, target_agent.armor)
            target_agent.armor -= damage_to_armor
            damage_to_health = 20 - damage_to_armor
        else:
            damage_to_health = 20
        target_agent.health -= damage_to_health
    
        if target_agent.health <= 0:
            target_agent.health = 0
            utils.remove_agent(target_agent, all_agents)


    def check_enemies_in_fov(self, all_agents):
        detected_agents = []

        for agent in all_agents:
            if agent != self:
                direction_to_agent = (agent.position - self.position).normalize()
                distance_to_agent = self.position.distance_to(agent.position)

                if distance_to_agent <= self.fov_range:
                    angle_to_agent = self.vision_vector.angle_to(direction_to_agent)
                    if abs(angle_to_agent) <= self.fov_angle / 2:
                        if not self.check_line_of_sight(self.position, agent.position):
                            detected_agents.append(agent)

        return detected_agents
    
    def identify_attacker(self, all_agents):
        closest_enemy = None
        min_distance = float('inf')
        for agent in all_agents:
            if agent != self:
                distance = self.position.distance_to(agent.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = agent
        return closest_enemy

    def rotate_vision(self, target):
        target_vector = pygame.Vector2(target.position[0] - self.position[0],
                                    target.position[1] - self.position[1])
        if target_vector.length() > 0:
            self.vision_vector = target_vector.normalize()

    def check_line_of_sight(self, start_position, end_position):
        direction = (end_position - start_position).normalize()
        max_distance = start_position.distance_to(end_position)
        intersection = utils.cast_ray(start_position, direction, max_distance)

        if intersection:
            return start_position.distance_to(intersection) < max_distance
        return False
    
    def seek_last_known_position(self):
        if self.last_known_enemy_pos:
            direction_to_target = (self.last_known_enemy_pos - self.position).normalize()
            self.vision_vector = direction_to_target
            self.velocity = direction_to_target * self.max_speed

            if self.position.distance_to(self.last_known_enemy_pos) < self.react_radius:
                self.last_known_enemy_pos = None
        
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

    