import pygame
import entity
import constants

pygame.init()
pygame.display.set_caption("Zombie attack")

player = entity.Player([constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2])
zombies = [
    entity.Agent((520,440)),
    entity.Agent((500,420)),
    entity.Agent((480,400)),
    entity.Agent((520,400)),
    entity.Agent((500,440)),
    entity.Agent((480,420))
]


def draw_obstacles():
    for obstacle_pos in constants.OBSTACLES_POS:
        obstacle = entity.Obstacle(obstacle_pos[0], obstacle_pos[1])
        obstacle.draw()


def draw_zombies():
    for zombie in zombies:
        zombie.update(30)
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

    constants.SCREEN.fill((0, 0, 0))

    draw_obstacles()
    draw_zombies()
    keys = pygame.key.get_pressed()
    draw_player(current_time, keys)

    pygame.display.flip()
    constants.CLOCK.tick(60)
