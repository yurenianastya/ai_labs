import pygame
import math
import steering_behaviors as sb
import utils


class Player():

    def __init__(self, initial_pos, obstacles):
        self.base_points = [
            pygame.Vector2(0, -20),
            pygame.Vector2(-10, 10),
            pygame.Vector2(10, 10)
        ]
        self.points = list(self.base_points)
        self.position = pygame.Vector2(initial_pos)
        self.prev_position = pygame.Vector2(initial_pos) # To track previous position for velocity
        self.velocity = pygame.Vector2(0,0)
        self.heading = pygame.Vector2(1,0)
        self.angle = 0
        self.speed = 5
        self.bullets = []
        self.bullet_speed = 10
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()
        self.obstacles = obstacles

    
    def get_movement_keys(self, keys, current_time):
        rotation_speed = 5
        original_position = self.position.copy()  
        
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
        else:
            self.velocity = pygame.Vector2(0, 0) 

        if self.check_collision_with_obstacles():
            self.position = original_position 

        self.velocity = self.position - self.prev_position
        self.rotate_player()
        
        if keys[pygame.K_SPACE]:
            if current_time - self.last_shot > self.shoot_delay:
                self.shoot_bullet()
                self.last_shot = current_time
    

    def update_heading(self):
        if self.velocity.length_squared() > 0:
            self.heading = self.velocity.normalize()

    
    def check_collision_with_obstacles(self):
        for obstacle in self.obstacles:
            distance = self.position.distance_to(obstacle.position)
            if distance < obstacle.radius:
                return True
        return False
    

    def check_collision_with_zombies(self, zombies):
        for zombie in zombies:
            distance = self.position.distance_to(zombie.position)
            if distance < zombie.radius + 15:
                return True
        return False
    

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

    
    def update_bullets(self, zombies):
        for bullet in self.bullets[:]:
            bullet["pos"][0] += bullet["dir"][0]
            bullet["pos"][1] += bullet["dir"][1]
            if (0 <= bullet["pos"][0] <= utils.SCREEN_WIDTH) and (0 <= bullet["pos"][1] <= utils.SCREEN_HEIGHT):
                pygame.draw.circle(utils.SCREEN, utils.COLOR_BULLET, (int(bullet["pos"][0]), int(bullet["pos"][1])), 3)
            else:
                self.bullets.remove(bullet) 
            self.check_bullet_collision_with_obstacles()


    def check_bullet_collision_with_obstacles(self):
        for bullet in self.bullets[:]:
            for obstacle in self.obstacles:
                distance = pygame.Vector2(bullet["pos"][0], bullet["pos"][1]).distance_to(obstacle.position)
                if distance <= obstacle.radius:
                    self.bullets.remove(bullet)
                    break


    def check_bullet_collision_with_zombies(self, zombies):
        for zombie in zombies[:]:
            for bullet in self.bullets:
                distance = pygame.Vector2(bullet["pos"][0], bullet["pos"][1]).distance_to(zombie.position)
                if distance < zombie.radius:
                    zombies.remove(zombie)
                    self.bullets.remove(bullet)
                    break


    def wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)

    
    def draw_and_update(self, current_time, zombies, keys):
        self.draw_direction_vector()
        self.get_movement_keys(keys, current_time)
        self.update_heading()
        pygame.draw.polygon(utils.SCREEN, utils.COLOR_PLAYER, [(p.x, p.y) for p in self.points])
        self.update_bullets(zombies)
        self.wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)


class Zombie:

    def __init__(self, position):
        self.position = position
        self.radius = utils.ZOMBIE_RADIUS
        self.velocity = pygame.Vector2(1,0)
        self.heading = pygame.Vector2()
        self.smoothed_heading = pygame.Vector2()
        self.acceleration = pygame.Vector2()
        self.side = pygame.Vector2()
        self.mass = 1.0
        self.max_turn_rate = 0.5 # radians per second
        self.max_speed = 0.1
        self.state = sb.SteeringBehaviors(self)
        self.wander_target = pygame.Vector2(1, 0)
        self.color = utils.COLOR_GREEN

         
    def draw(self):
        pygame.draw.circle(utils.SCREEN, self.color, self.position, self.radius)


    def wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)


    def tag_neighbors(self, objects, radius):
        tagged_neighbors = []
        for obj in objects:
            if obj == self:
                continue
            distance_squared = self.position.distance_squared_to(obj.position)
            if distance_squared < (radius ** 2):
                tagged_neighbors.append(obj)
        return tagged_neighbors


    def update(self, time_elapsed, zombies, obstacles, player):
        steering_force = self.state.calculate(self.tag_neighbors(zombies, utils.NEIGHBOR_RADIUS), obstacles, player)
        # acceleration = force / mass
        self.acceleration = steering_force / self.mass
        self.velocity += self.acceleration * time_elapsed
        if self.velocity.length() > self.max_speed:
            self.velocity = utils.truncate(self.velocity, self.max_speed)
        self.position += self.velocity * time_elapsed
        if self.velocity.length_squared() > 0.000001:
            self.heading = self.velocity.normalize()
            self.side = utils.perp(self.heading)
        self.wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)


class Obstacle():

    # position (x,y) and radius
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

    
    def draw(self):
        pygame.draw.circle(utils.SCREEN, utils.COLOR_OBSTACLES,
                            (int(self.position[0]), int(self.position[1])), self.radius)