import pygame
import math
import steering_behaviors as sb
import utils


class Player():

    def __init__(self, initial_pos, obstacles):
        self.base_shape = [
            pygame.Vector2(0, -20),
            pygame.Vector2(-10, 10),
            pygame.Vector2(10, 10)
        ]
        self.points = list(self.base_shape)
        self.position = pygame.Vector2(initial_pos)
        self.prev_position = pygame.Vector2(initial_pos)
        self.velocity = pygame.Vector2(0,0)
        self.heading = pygame.Vector2(1,0)
        self.angle = 0
        self.speed = 4
        self.bullets = []
        self.bullet_speed = 10
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()
        self.obstacles = obstacles
    

    def handle_input(self, keys, current_time):
        self._rotate(keys)
        self._move(keys)
        if keys[pygame.K_SPACE] and current_time - self.last_shot > self.shoot_delay:
            self.shoot_bullet()
            self.last_shot = current_time

    def _rotate(self, keys):
        rotation_speed = 5
        if keys[pygame.K_LEFT]:
            self.angle += rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= rotation_speed

    def _move(self, keys):
        direction = pygame.Vector2(math.cos(math.radians(self.angle)),
                                   -math.sin(math.radians(self.angle)))
        original_position = self.position.copy()
        if keys[pygame.K_UP]:
            self.position += direction * self.speed
        elif keys[pygame.K_DOWN]:
            self.position -= direction * self.speed

        if self._check_collision_with_obstacles():
            self.position = original_position
        self.velocity = self.position - original_position
    

    def update_heading(self):
        if self.velocity.length_squared() > 0:
            self.heading = self.velocity.normalize()

    
    def _check_collision_with_obstacles(self):
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
    

    def _rotate_shape(self):
        cos_theta = math.cos(math.radians(self.angle))
        sin_theta = math.sin(math.radians(self.angle))
        self.shape = [
            pygame.Vector2(
                point.x * sin_theta - point.y * cos_theta,
                point.x * cos_theta + point.y * sin_theta
            ) + self.position
            for point in self.base_shape
        ]

    def _draw_direction_vector(self):
        length = 20
        end_pos = (
            self.shape[0].x + length * math.cos(math.radians(self.angle)),
            self.shape[0].y - length * math.sin(math.radians(self.angle)),
        )
        pygame.draw.line(utils.SCREEN, utils.COLORS['GUN'], self.shape[0], end_pos, 3)


    def shoot_bullet(self):
        rad = math.radians(self.angle)
        bullet_velocity = pygame.Vector2(
            self.bullet_speed * math.cos(rad),
            -self.bullet_speed * math.sin(rad)
        )
        self.bullets.append({"pos": self.position.copy(), "dir": bullet_velocity})

    
    def _update_bullets(self):
        for bullet in self.bullets[:]:
            bullet["pos"][0] += bullet["dir"][0]
            bullet["pos"][1] += bullet["dir"][1]
            
            if not (0 <= bullet["pos"][0] <= utils.SCREEN_WIDTH) or not (0 <= bullet["pos"][1] <= utils.SCREEN_HEIGHT):
                self.bullets.remove(bullet)
            else:
                self._check_bullet_collision_with_obstacles(bullet)


    def _draw_bullets(self):
        for bullet in self.bullets:
            pygame.draw.circle(utils.SCREEN, utils.COLORS['BULLET'], (int(bullet["pos"].x), int(bullet["pos"].y)), 3)



    def _check_bullet_collision_with_obstacles(self, bullet):
        for obstacle in self.obstacles:
            if bullet["pos"].distance_to(obstacle.position) <= obstacle.radius:
                self.bullets.remove(bullet)
                break


    def _check_zombie_collisions(self, zombies):
        for zombie in zombies[:]:
            for bullet in self.bullets[:]:
                if bullet["pos"].distance_to(zombie.position) < zombie.radius:
                    zombies.remove(zombie)
                    self.bullets.remove(bullet)
                    break


    def _wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)

    
    def update(self, current_time, zombies, keys):
        self.handle_input(keys, current_time)
        self._update_bullets()
        self._check_zombie_collisions(zombies)
        self._wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)

    
    def draw(self):
        self._rotate_shape()
        pygame.draw.polygon(utils.SCREEN, utils.COLORS['PLAYER'], [(p.x, p.y) for p in self.shape])
        self._draw_direction_vector()
        self._draw_bullets()


class Zombie:
    
    def __init__(self, position):
        self.color = utils.COLORS['ZOMBIE']
        self.position = pygame.Vector2(position)
        self.radius = utils.ZOMBIE_RADIUS
        self.velocity = pygame.Vector2(1,0)
        self.heading = pygame.Vector2(1,0)
        self.side = Zombie.perp(self.heading)
        self.max_speed = 0.08
        self.mass = 1.0
        self.state = sb.SteeringBehaviors(self)
        self.wander_target = pygame.Vector2(1,0)
        self.max_turn_rate = 0.1
        self.force_smoother = sb.ExponentialSmoother(alpha=0.2)


    def _wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)


    def tag_neighbors(self, objects, radius):
        tagged_neighbors = []
        for obj in objects:
            to = obj.position - self.position
            total_radius = radius + obj.radius
            if obj != self and to.length_squared() < total_radius*total_radius:
                tagged_neighbors.append(obj)
        return tagged_neighbors


    def update(self, time_elapsed, obstacles, player, zombies):
        steering_force = self.state.calculate(obstacles, player, zombies)
        self.velocity += (steering_force / self.mass) * time_elapsed
        self.velocity = utils.truncate(self.velocity, self.max_speed)
        self.heading = self.velocity.normalize()
        self.position += self.velocity * time_elapsed
        self._wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)
        

    def draw(self):
        pygame.draw.circle(utils.SCREEN, self.color, self.position, self.radius)

    
    def perp(vec):
        return pygame.Vector2(-vec.y, vec.x)

class Obstacle():

    def __init__(self, position, radius):
        self.position = pygame.Vector2(position)
        self.radius = radius

    
    def draw(self):
        pygame.draw.circle(utils.SCREEN, utils.COLORS['OBSTACLES'],
                            (int(self.position.x), int(self.position.y)), self.radius)