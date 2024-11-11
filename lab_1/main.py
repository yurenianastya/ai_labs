import pygame
import entity
import utils

pygame.init()
pygame.display.set_caption("Zombie attack")
pygame.display.set_mode((0,0), pygame.FULLSCREEN)

player = entity.Player([utils.SCREEN_WIDTH // 2, utils.SCREEN_HEIGHT // 2])

def draw_obstacles():
    for obstacle in utils.obstacles:
        obstacle.draw()


def draw_zombies():
    for zombie in entity.zombies:
        zombie.update(30, entity.zombies, player)
        zombie.draw()

    
def draw_player(current_time, keys):
    player.draw_and_update(current_time, keys)


# Game running
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    utils.SCREEN.fill((0, 0, 0))

    draw_obstacles()
    draw_zombies()
    keys = pygame.key.get_pressed()
    draw_player(current_time, keys)

    pygame.display.flip()
    utils.CLOCK.tick(60)
