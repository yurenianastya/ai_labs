import pygame
import pygame.gfxdraw
import graph
import utils
import raven


pygame.init()
map_graph = graph.Graph()
map_graph.generate_graph()

BOTS = [
    raven.RavenBot(
        map_graph.nodes.get(45),
        map_graph
    ),
    raven.RavenBot(
        map_graph.nodes.get(3100),
        map_graph
    ),
    raven.RavenBot(
        map_graph.nodes.get(500),
        map_graph
    ),
    raven.RavenBot(
        map_graph.nodes.get(1200),
        map_graph
    ),
]


def draw_graph(graph, surface):
    for node in graph.nodes:
        for edge in graph.edges[node]:
            from_x, from_y = graph.nodes[edge.from_node].x, graph.nodes[edge.from_node].y
            to_x, to_y = graph.nodes[edge.to_node].x, graph.nodes[edge.to_node].y
            pygame.draw.line(surface, utils.EDGE_COLOR, (from_x, from_y), (to_x, to_y), 1)
    
    for node in graph.nodes.values():
        x, y = node.x, node.y
        pygame.draw.circle(surface, utils.NODE_COLOR, (x, y), 2)
    

def draw_path(path, surface, start_node, goal_node):
    if path and len(path) > 1:
        points = [(node.x, node.y) for node in path]
        pygame.draw.lines(surface, (0,0,0), False, points, 5)

    pygame.draw.circle(surface, utils.BOT_COLOR, (start_node.x, start_node.y), 8)
    pygame.draw.circle(surface, utils.EDGE_COLOR, (goal_node.x, goal_node.y), 8)


def draw_bots_fov_cone(bot, screen):
    forward_vector = bot.velocity.normalize() if bot.velocity.length() > 0 else pygame.Vector2(1, 0)
    left_vector = forward_vector.rotate(bot.fov_angle / 2) * bot.fov_range
    right_vector = forward_vector.rotate(-bot.fov_angle / 2) * bot.fov_range

    fov_color = (100, 100, 255, 80)
    pygame.gfxdraw.filled_polygon(
        screen, [
            (int(bot.position.x), int(bot.position.y)),
            (int(bot.position.x + left_vector.x), int(bot.position.y + left_vector.y)),
            (int(bot.position.x + right_vector.x), int(bot.position.y + right_vector.y))
        ],
        fov_color
    )

def draw_bots(bots, surface):
    for bot in bots:
        pygame.draw.circle(surface, utils.BOT_COLOR, bot.position, bot.radius)
        draw_bots_fov_cone(bot, surface)


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
    return True

for bot in BOTS:
    bot.calculate_path()

running = True
while running:
    running = handle_events()
    if not running:
        break

    dt = utils.CLOCK.tick(60) / 1000.0
    
    for bot in BOTS:
        bot.update(dt, BOTS)

    utils.SCREEN.fill(utils.MAP_COLOR)

    utils.create_and_draw_obstacles()
    draw_graph(map_graph, utils.SCREEN)
    draw_bots(BOTS, utils.SCREEN)

    pygame.display.flip()


pygame.quit()