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
        self.speed = 3
        self.bullets = []
        self.bullet_speed = 10
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()
        self.obstacles = obstacles  # Об'єкти перешкод

    
    def get_movement_keys(self, keys, current_time):
        rotation_speed = 5
        original_position = self.position.copy()  # Зберігаємо початкову позицію

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
        # Перевірка зіткнення з усіма перешкодами
        for obstacle in self.obstacles:
            distance = self.position.distance_to(obstacle.position)
            if distance < obstacle.radius:
                return True  # Якщо є зіткнення
        return False  # Якщо зіткнення немає
    
    def check_collision_with_zombies(self, zombies):
            for zombie in zombies:
                    distance = self.position.distance_to(zombie.position)
                    if distance < zombie.radius + 15:  # Додаємо 10, бо гравець має розмір
                        return True  # Якщо є зіткнення з зомбі
            return False  # Якщо зіткнення немає    
    
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
            self.check_bullet_collision_with_obstacles()
    


    def check_bullet_collision_with_obstacles(self):
        for bullet in self.bullets[:]:
            for obstacle in self.obstacles:
                distance = pygame.Vector2(bullet["pos"][0], bullet["pos"][1]).distance_to(obstacle.position)
                if distance <= obstacle.radius:  # Якщо пуля торкається перешкоди
                    self.bullets.remove(bullet)  # Видаляємо кулю
                    break       
    def check_bullet_collision_with_zombies(self, zombies):
        for zombie in zombies[:]:
            for bullet in self.bullets:
                distance = pygame.Vector2(bullet["pos"][0], bullet["pos"][1]).distance_to(zombie.position)
                if distance < zombie.radius:  # Якщо пуля потрапила в зомбі
                    print(f"Пуля потрапила в зомбі на позиції {zombie.position}")
                    zombies.remove(zombie)  # Видаляємо зомбі зі списку
                    self.bullets.remove(bullet)  # Видаляємо кулю
                    break
        
        
    def wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)

    
    def draw_and_update(self, current_time, keys):
        self.draw_direction_vector()
        self.get_movement_keys(keys, current_time)
        self.update_heading()
        pygame.draw.polygon(utils.SCREEN, utils.COLOR_PLAYER, [(p.x, p.y) for p in self.points])
        self.update_bullets()
        self.wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)


class Zombie:

    def __init__(self, position):
        self.position = position
        self.radius = 7
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
        self.smoothing = 0.2
        # #self.is_visible = True
        # self.is_dead = False  # Спочатку зомбі живий
        # self.death_time = None  # Час смерті, використовується для відродження
    
    # def kill(self, current_time):
    #     self.is_dead = True
    #     self.is_visible = False
    #     print(f"Zombie at {self.position} marked as dead with is_dead={self.is_dead} and visibility is {self.is_visible}")
    #     self.death_time = current_time  # Фіксуємо час смерті
    #     self.draw()
        

    #def respawn(self, current_time):
    #    if self.is_dead and current_time - self.death_time >= 50000:  
    #        self.is_dead = False
    #        self.is_visible = True
    #        print(f"Zombie at {self.position} marked as alive with is_dead={self.is_dead} and visibility is {self.is_visible} and death time={self.death_time} ")
             
    def draw(self):
            pygame.draw.circle(utils.SCREEN, utils.COLOR_ZOMBIE, self.position, self.radius)

    def perp(vec):
        return pygame.Vector2(-vec.y, vec.x)
    
    def lerp(self, start, end, alpha):
        return start + (end - start) * alpha

    def wrap_around(self, max_x, max_y):
        self.position.x = self.position.x % (max_x + 1)
        self.position.y = self.position.y % (max_y + 1)
    

    def tag_neighbors(self, zombies, radius):
        neighbors = []
        for zombie in zombies:
            vector_to = zombie.position - self.position
            tag_range = zombie.radius + radius
            if zombie != self and vector_to.length_squared() < tag_range ** 2:
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
            desired_heading = self.velocity.normalize()
            self.heading = self.lerp(self.heading, desired_heading, self.smoothing)
            self.side = Zombie.perp(self.heading)
        self.wrap_around(utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT)


zombies = [ Zombie(pos) for pos in utils.ZOMBIES_POS ]