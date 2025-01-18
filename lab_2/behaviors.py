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


    def flee(self, target_position):
        desired_velocity = self.agent.position - target_position
        if desired_velocity.length() > 0:
            desired_velocity = desired_velocity.normalize() * self.agent.max_speed
            steering = desired_velocity - self.agent.velocity
            return steering
        else:
            return pygame.Vector2(0, 0)
        

class State:

    def __init__(self, agent):
        self.agent = agent

    def enter(self):
        pass

    def exit(self):
        pass

    def execute(self, dt):
        pass