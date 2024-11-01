import pygame
import steering_behaviors as sb


class Player():


    def __init__(self, position):
        self.position = position
        self.speed = 0
        self.velocity = pygame.math.Vector2()


class Agent:

    def __init__(self, position):
        self.position = position
        self.velocity = pygame.Vector2()
        self.heading = pygame.Vector2()
        self.acceleration = pygame.Vector2()
        self.side = pygame.Vector2()
        self.mass = 1.0
        self.max_turn_rate = 0.5 # radians per second
        self.max_speed = 0.1
        self.state = sb.SteeringBehaviors(self)

    
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


    def update(self, time_elapsed):
        steering_force = self.state.arrive((50,50), sb.Deceleration.FAST.value)
        # acceleration = force / mass
        self.acceleration = steering_force / self.mass
        self.velocity += self.acceleration * time_elapsed
        if self.velocity.length() > self.max_speed:
            self.truncate(self.velocity, self.max_speed)
        self.position += self.velocity * time_elapsed
        if self.velocity.length_squared() > 0.000001:
            self.heading = self.velocity.normalize()
            self.side = self.perp(self.heading)
