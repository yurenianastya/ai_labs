import pygame
import math
import steering_behaviors as sb
import utils


class Player():

    def __init__(self, initial_pos):
        self.base_points = [
            pygame.Vector2(0, -20),
            pygame.Vector2(-10, 10),
            pygame.Vector2(10, 10)
        ]
        self.points = list(self.base_points)
        self.position = pygame.Vector2(initial_pos)
        self.prev_position = pygame.Vector2(initial_pos) # To track previous position for velocity
        self.velocity = pygame.Vector2(0,0)
        self.angle = 0
        self.speed = 3
        self.bullets = []
        self.bullet_speed = 10
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()

    
    def get_movement_keys(self, keys, current_time):
        rotation_speed = 5
        
        if keys[pygame.K_LEFT]:
            self.angle += rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= rotation_speed

        rad_angle = math.radians(self.angle)
        self.prev_position = self.position.copy()

        if keys[pygame.K_UP]:
            self.position.x += self.speed * math.cos(rad_angle)
            self.position.y -= self.speed * math.sin(rad_angle)
        if keys[pygame.K_DOWN]:
            self.position.x -= self.speed * math.cos(rad_angle)
            self.position.y += self.speed * math.sin(rad_angle)

        self.velocity = self.position - self.prev_position
        self.rotate_player()
        
        if keys[pygame.K_SPACE]:
            if current_time - self.last_shot > self.shoot_delay:
                self.shoot_bullet()
                self.last_shot = current_time

    
    def rotate_player(self):
        cos_theta = math.cos(math.radians(self.angle))
        sin_theta = math.sin(math.radians(self.angle))
        
        self.points = [
            pygame.Vector2(
                p.x * sin_theta - p.y * cos_theta,
                p.x * cos_theta + p.y * sin_theta
                ) + self.position
            for p in self.base_points
        ]

    def draw_direction_vector(self):
        length = 20
        width = 3
        end_pos = (
            self.points[0].x + length * math.cos(math.radians(self.angle)),
            self.points[0].y - length * math.sin(math.radians(self.angle)),
        )
        pygame.draw.line(utils.SCREEN, utils.COLOR_GUN, self.points[0], end_pos, width)


    def shoot_bullet(self):
        rad = math.radians(self.angle)
        dx = self.bullet_speed * math.cos(rad)
        dy = -self.bullet_speed * math.sin(rad)
        self.bullets.append({"pos": list(self.position), "dir": (dx, dy)})

    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet["pos"][0] += bullet["dir"][0]
            bullet["pos"][1] += bullet["dir"][1]
            if (0 <= bullet["pos"][0] <= utils.SCREEN_WIDTH) and (0 <= bullet["pos"][1] <= utils.SCREEN_HEIGHT):
                pygame.draw.circle(utils.SCREEN, utils.COLOR_BULLET, (int(bullet["pos"][0]), int(bullet["pos"][1])), 3)
            else:
                self.bullets.remove(bullet) 

    
    def wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)

    
    def draw_and_update(self, current_time, keys):
        self.draw_direction_vector()
        self.get_movement_keys(keys, current_time)
        pygame.draw.polygon(utils.SCREEN, utils.COLOR_PLAYER, [(p.x, p.y) for p in self.points])
        self.update_bullets()
        self.wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)


class Zombie:

    def __init__(self, position):
        self.position = position
        self.radius = 7
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
        pygame.draw.circle(utils.SCREEN, utils.COLOR_ZOMBIE, self.position, self.radius)


    def perp(vec):
        return pygame.Vector2(-vec.y, vec.x)
    

    def wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)
    

    def tag_neighbors(self, zombies, radius):
        neighbors = []
        for zombie in zombies:
            vector_to = zombie.position - self.position
            range = zombie.radius + radius
            if zombie != self and vector_to.length_squared() < range ** 2:
                neighbors.append(zombie)
        return neighbors


    def update(self, time_elapsed, zombies, player):
        steering_force = self.state.calculate(self.tag_neighbors(zombies, utils.NEIGHBOR_RADIUS), player)
        # acceleration = force / mass
        self.acceleration = steering_force / self.mass
        self.velocity += self.acceleration * time_elapsed
        if self.velocity.length() > self.max_speed:
            utils.truncate(self.velocity, self.max_speed)
        self.position += self.velocity * time_elapsed
        if self.velocity.length_squared() > 0.000001:
            self.heading = self.velocity.normalize()
            self.side = Zombie.perp(self.heading)
        self.wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)


zombies = [ Zombie(pos) for pos in utils.ZOMBIES_POS ]