import pygame
import steering_behaviors as sb
import constants

class Obstacle():

    # position (x,y) and radius
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

    
    def draw(self):
        pygame.draw.circle(constants.SCREEN, constants.COLOR_OBSTACLES,
                            (int(self.position[0]), int(self.position[1])), self.radius)


class Agent:

    def __init__(self, position):
        self.position = position
        self.velocity = pygame.Vector2(1,0)
        self.heading = pygame.Vector2()
        self.acceleration = pygame.Vector2()
        self.side = pygame.Vector2()
        self.mass = 1.0
        self.max_turn_rate = 0.5 # radians per second
        self.max_speed = 0.05
        self.state = sb.SteeringBehaviors(self)
        self.wander_target = pygame.Vector2(1, 0)

    
    def draw(self):
        pygame.draw.circle(constants.SCREEN, constants.COLOR_RED, self.position, 10)

    
    def truncate(self, vec, max_len):
        current_len = vec.length()
        if current_len > max_len:
            scale = max_len / current_len
            vec.x *= scale
            vec.y *= scale
    

    def perp(self, vec):
        return pygame.Vector2(-vec.y, vec.x)


    def wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)

    
    def get_obstacles(self):
        obstacle_objects = [Obstacle(position,radius) for position, radius in constants.OBSTACLES_POS]
        return obstacle_objects


    def update(self, time_elapsed):
        steering_force = self.state.calculate(self.get_obstacles())
        # acceleration = force / mass
        self.acceleration = steering_force / self.mass
        self.velocity += self.acceleration * time_elapsed
        if self.velocity.length() > self.max_speed:
            self.truncate(self.velocity, self.max_speed)
        self.position += self.velocity * time_elapsed
        if self.velocity.length_squared() > 0.000001:
            self.heading = self.velocity.normalize()
            self.side = self.perp(self.heading)
        self.wrap_around(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
