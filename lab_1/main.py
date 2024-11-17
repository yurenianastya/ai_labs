import pygame
import entity
import utils

pygame.init()
pygame.display.set_caption("Zombie attack")
pygame.display.set_mode((utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT))
font = pygame.font.SysFont("Arial", 36)

obstacles = [ entity.Obstacle(pos, rad) for pos, rad in utils.OBSTACLES_POS ]
player = entity.Player([utils.SCREEN_WIDTH // 2, utils.SCREEN_HEIGHT // 2], obstacles)
zombies = [ entity.Zombie(pos) for pos in utils.ZOMBIES_POS ]

def draw_obstacles():
    for obstacle in obstacles:
        obstacle.draw()


def draw_zombies():
    for zombie in zombies:
        zombie.update(30, zombies, obstacles, player)
        zombie.draw()

    
def draw_player(current_time, keys):
    player.draw_and_update(current_time, zombies, keys)


# Game running
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    utils.SCREEN.fill((0, 0, 0))

    if player.check_collision_with_zombies(zombies):
        win_text = font.render("You are dead!", True, (255, 255, 255))
        utils.SCREEN.blit(win_text, (utils.SCREEN_WIDTH // 2 - win_text.get_width() // 2, utils.SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False
    if  len(zombies) == 0:
        win_text = font.render("All the zombies are killed!", True, (255, 255, 255))
        utils.SCREEN.blit(win_text, (utils.SCREEN_WIDTH // 2 - win_text.get_width() // 2, utils.SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    draw_obstacles()
    player.check_bullet_collision_with_zombies(zombies)
    draw_zombies()
    keys = pygame.key.get_pressed()
    draw_player(current_time, keys)

    pygame.display.flip()
    utils.CLOCK.tick(30)
