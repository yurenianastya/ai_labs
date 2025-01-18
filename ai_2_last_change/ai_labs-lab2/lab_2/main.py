import random
import pygame
import pygame.gfxdraw
import graph
import utils
import entity


pygame.init()
map_graph = graph.Graph()
map_graph.generate_graph()

agents = [
    entity.Agent(
        map_graph.nodes.get(45),
        map_graph,
        sorted(utils.WANDER_NODES_IDX, key=lambda x: random.random())
    ),
    entity.Agent(
        map_graph.nodes.get(3100),
        map_graph,
        sorted(utils.WANDER_NODES_IDX, key=lambda x: random.random())
    ),
    entity.Agent(
        map_graph.nodes.get(500),
        map_graph,
        sorted(utils.WANDER_NODES_IDX, key=lambda x: random.random())
    ),
    entity.Agent(
        map_graph.nodes.get(1200),
        map_graph,
        sorted(utils.WANDER_NODES_IDX, key=lambda x: random.random())
    ),
]

items = entity.PickupItem.generate_items(map_graph)

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

    pygame.draw.circle(surface, utils.AGENT_COLOR, (start_node.x, start_node.y), 8)
    pygame.draw.circle(surface, utils.EDGE_COLOR, (goal_node.x, goal_node.y), 8)


def draw_agents_fov_cone(agent, screen):
    forward_vector = agent.velocity.normalize() if agent.velocity.length() > 0 else pygame.Vector2(1, 0)
    left_vector = forward_vector.rotate(agent.fov_angle / 2) * agent.fov_range
    right_vector = forward_vector.rotate(-agent.fov_angle / 2) * agent.fov_range

    fov_color = (100, 100, 255, 80)
    pygame.gfxdraw.filled_polygon(
        screen, [
            (int(agent.position.x), int(agent.position.y)),
            (int(agent.position.x + left_vector.x), int(agent.position.y + left_vector.y)),
            (int(agent.position.x + right_vector.x), int(agent.position.y + right_vector.y))
        ],
        fov_color
    )

def draw_agents(agents, surface):
    for agent in agents:
        pygame.draw.circle(surface, utils.AGENT_COLOR, agent.position, agent.radius)
        draw_agents_fov_cone(agent, surface)
        draw_hit_bars(agent, surface)

def draw_shots(surface, dt):
    # Копіюємо список, щоб уникнути проблем із модифікацією
    shots_to_draw = utils.SHOTS[:]
    for shot in shots_to_draw:
        start_pos, end_pos, time_left = shot
        pygame.draw.line(surface, (255, 0, 0), start_pos, end_pos, 2)
        utils.SHOTS.remove(shot)
        if time_left > dt:
            utils.SHOTS.append((start_pos, end_pos, time_left - dt))


def draw_item(item, surface):
        x = item.position.x
        y = item.position.y
        if item.item_type == "health":
            radius = 13
            pygame.draw.circle(surface, (0, 100, 0), (item.position), radius)
            pygame.draw.line(surface, (255, 255, 255), (x - radius // 2, y),
             (x + radius // 2, y), 5)
            pygame.draw.line(surface, (255, 255, 255), (x, y - radius // 2 ),
             (x, y + radius // 2), 5)
        elif item.item_type == "armor":
            pygame.draw.rect(surface, (0, 0, 255), (x - 12, y - 10, 24, 20))
            pygame.draw.polygon(surface, (0, 0, 255), [
                (x - 12, y + 10), 
                (x + 12, y + 10),
                (x + 8, y + 20),
                (x - 8, y + 20)
            ])
            pygame.draw.rect(surface, (255, 255, 255), (x - 9, y - 7, 18, 14))
            pygame.draw.polygon(surface, (255, 255, 255), [
                (x - 9, y + 7),
                (x + 9, y + 7),
                (x + 6, y + 14),
                (x - 6, y + 14)
            ])  
            pygame.draw.rect(surface, (0, 0, 255), (x - 6, y - 4, 12, 8))
            pygame.draw.polygon(surface, (0, 0, 255), [
                (x - 6, y + 4),
                (x + 6, y + 4),
                (x + 4, y + 8),
                (x - 4, y + 8)
            ])

def draw_hit_bars(bot, surface):
    bar_width = 40
    bar_height = 5
    health_bar_x = bot.position.x - bar_width // 2
    health_bar_y = bot.position.y - 20  
    armor_bar_y = health_bar_y - 8
    health_percent = bot.health / bot.max_health
    pygame.draw.rect(surface, (100, 100, 100), (health_bar_x, health_bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 255, 0), (health_bar_x, health_bar_y, int(bar_width * health_percent), bar_height)) 
    armor_percent = bot.armor / bot.max_armor
    pygame.draw.rect(surface, (50, 50, 50), (health_bar_x, armor_bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 200, 255), (health_bar_x, armor_bar_y, int(bar_width * armor_percent), bar_height))  

def draw_pickup_items(items, surface):
    for item in items:
        draw_item(item, surface)
    
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
    return True

def check_agent_on_item(agent, items):
    for item in items:
        if abs(agent.position.x - item.position.x) <= 3 and abs(agent.position.y - item.position.y) <= 3:
            if item.item_type == "health":
                agent.health = min(agent.max_health, agent.health + 20)
                print(f"Бот {agent} отримав +20 здоров'я. Поточне: {agent.health}")
            elif item.item_type == "armor":
                agent.pick_up_armor()  # Збільшуємо броню
                print(f"Бот {agent} отримав броню.")
            item.respawn()

for agent in agents:
    agent.calculate_path()

running = True
while running:
    running = handle_events()
    if not running:
        break

    dt = utils.CLOCK.tick(60) / 1000.0
    for agent in agents:
        agent.update(dt, agents)
        check_agent_on_item(agent, items)

    utils.SCREEN.fill(utils.MAP_COLOR)

    utils.create_and_draw_obstacles()
    draw_graph(map_graph, utils.SCREEN)
    draw_agents(agents, utils.SCREEN)
    draw_pickup_items(items, utils.SCREEN)
    draw_shots(utils.SCREEN, dt)
    pygame.display.flip()


pygame.quit()