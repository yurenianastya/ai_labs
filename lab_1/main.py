import pygame
import entity
import utils

pygame.init()
pygame.display.set_caption("Zombie attack")
pygame.display.set_mode((utils.SCREEN_WIDTH, utils.SCREEN_HEIGHT))
font = pygame.font.SysFont("Arial", 36)

obstacles = [entity.Obstacle(data["position"], data["radius"]) for data in utils.OBSTACLES]
player = entity.Player([30, 30], obstacles)
zombies = [ entity.Zombie(pos) for pos in utils.ZOMBIES ]


def draw_obstacles():
    for obstacle in obstacles:
        obstacle.draw()


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
    return True


def display_message(message):
    win_text = font.render(message, True, (255, 255, 255))
    utils.SCREEN.blit(win_text, (utils.SCREEN_WIDTH // 2 - win_text.get_width() // 2, utils.SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(1000)


def update_game_logic(current_time, zombies):
    keys = pygame.key.get_pressed()
    player.update(current_time, zombies, keys)
    for zombie in zombies:
        zombie.update(60, obstacles, player, zombies)
    #if player.check_collision_with_zombies(zombies):
        #display_message("You are dead!")
        #return False
    if not zombies:
        display_message("All the zombies are killed!")
        return False
    return zombies


def render_game(zombies):
    utils.SCREEN.fill((0, 0, 0))
    draw_obstacles()
    player.draw()
    for zombie in zombies:
        zombie.draw()
    pygame.display.flip()

running = True
while running:
    current_time = pygame.time.get_ticks()
    running = handle_events()
    if not running:
        break
    zombies = update_game_logic(current_time, zombies)
    if zombies is False:
        break
    render_game(zombies)
    utils.CLOCK.tick(60)