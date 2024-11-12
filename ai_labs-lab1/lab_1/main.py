import pygame
import entity
import utils

pygame.init()
pygame.display.set_caption("Zombie attack")
#pygame.display.set_mode((0,0), pygame.FULLSCREEN)

obstacles = [utils.Obstacle(pos, radius) for pos, radius in utils.OBSTACLES_POS]
player = entity.Player([utils.SCREEN_WIDTH // 2, utils.SCREEN_HEIGHT // 2], obstacles)
zombies = [entity.Zombie(pos) for pos in utils.ZOMBIES_POS]

def draw_obstacles():
    for obstacle in utils.obstacles:
        obstacle.draw()


def draw_zombies():
    current_time = pygame.time.get_ticks()
    for zombie in zombies:
        zombie.respawn(current_time)  # Перевірка відродження зомбі
        if not zombie.is_dead:
            zombie.update(30, zombies, player)
            zombie.draw()
    

    
def draw_player(current_time, keys):
    player.draw_and_update(current_time, keys)
    player.check_bullet_collision(zombies)  # Перевірка попадання кулі в зомбі



# Game running
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    utils.SCREEN.fill((0, 0, 0))

    if player.check_collision_with_zombies(zombies):
        print("Гравець зіткнувся з зомбі!")
        running = False  # Закриваємо гру

    draw_obstacles()
    draw_zombies()
    keys = pygame.key.get_pressed()
    draw_player(current_time, keys)

    pygame.display.flip()
    utils.CLOCK.tick(60)
