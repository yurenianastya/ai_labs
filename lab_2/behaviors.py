import pygame


class SteeringBehavior:

    def __init__(self, agent):
        self.agent = agent

    def calculate(self):
        total_force = pygame.Vector2(0, 0)

        seek_force = self.seek(self.agent.current_target.position)
            
        total_force += seek_force
        return total_force

    def seek(self, target_position):
        desired_velocity = target_position - self.agent.position
        if desired_velocity.length() > 0:
            desired_velocity = desired_velocity.normalize() * self.agent.max_speed
            steering = desired_velocity - self.agent.velocity
            return steering
        else:
            return pygame.Vector2(0, 0)
        

class FSM:

    def __init__(self, agent):
        self.agent = agent
        self.state = "random_walk"

    def calculate_state(self, all_agents):
        if self.agent.health <= 40 and self.agent.armor <= 20:
            return "seek_item"

        enemy_in_fov = self.agent.get_first_enemy_in_fov(all_agents)

        if enemy_in_fov:
            self.agent.target_enemy_node = enemy_in_fov.current_node
            self.agent.check_and_shoot(enemy_in_fov)
            return "fight"
        
        if self.agent.target_enemy_node:
            if self.agent.current_node == self.agent.target_enemy_node:
                self.agent.target_enemy_node = None
                return "random_walk"
            return "pursuit"
        
        self.agent.target_enemy_node = None

        return "random_walk"
    
    def update_state(self, all_agents):
        new_state = self.calculate_state(all_agents)

        if new_state != self.state:
            self.state = new_state
            self.agent.calculate_path()