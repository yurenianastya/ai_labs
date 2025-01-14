from collections import defaultdict
from typing import Optional
import pygame
import steering_behaviors as sb
import triggers
import graph
import utils

class RavenMap:

    def __init__(self, walls):
        self.walls = utils.WALLS
        self.trigger_sys = triggers.TriggerSystem()
        self.spawn_points = utils.SPAWN_POINTS
        self.nav_graph = graph.NavGraph()

    def update_trigger_sys(bots):
        pass


class RavenGame: 

    def __init__(self, map, bots, projectiles):
        self.map = map
        self.bots = bots
        # the user may select a bot to control manually. This variable points which one
        self.selected_bot = None
        # this list contains any active projectiles 
        self.projectiles = projectiles

    def update():
        pass

    def is_path_obstructed(vec_a, vec_b, bounding_radius=0):
        return False
    
    def get_all_bots_in_fov(bot):
        return []
    
    def if_second_visible_to_first(first_bot, second_bot):
        return False


class RavenBot:

    def __init__(self, spawn_node, graph):
        self.steering_behaviors = sb.SteeringBehavior(self)
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)
        self.velocity = pygame.Vector2(0, 0)
        self.graph = graph
        self.path = []
        self.current_target = None
        self.current_node = spawn_node
        self.goals = utils.WANDER_NODES_IDX
        self.goal_index = 0
        self.radius = 5
        self.react_radius = 10
        self.max_speed = 100

        # Health and armor attributes
        self.health = 100
        self.max_health = 100
        self.armor = 50
        self.max_armor = 50

        
    def update(self, dt):
        
        self.update_movement(dt)
        # if self.vision_update_regulator.is_ready():
        #     self.sensory_memory.update_vision()
        # if self.target_selection_regulator.is_ready():
        #     self.targeting_system.update()
        # if self.goal_arbitration_regulator.is_ready():
        #     self.brain.arbitrate()
        # if self.weapon_selection_regulator.is_ready():
        #     self.weapon_system.select_weapon()
        # self.weapon_system.take_aim_and_shoot()


    def update_movement(self, dt):
        
        if self.dynamic_condition_met():
            self.replan_path()
        

    def update_movement(self, dt):

        if not self.current_target and self.path:
            self.current_target = self.path.pop(0)

        if self.current_target:
            target_position = pygame.Vector2(self.current_target.position)
            steering_force = self.steering_behaviors.seek(target_position)
            self.velocity += steering_force 

            if self.velocity.length() > self.max_speed:
                self.velocity = self.velocity.normalize() * self.max_speed
            
            self.position += self.velocity * dt

            if self.position.distance_to(target_position) < self.react_radius:
                if self.path:
                    self.current_target = self.path.pop(0)
                else:
                    self.current_node = self.goals[self.goal_index]
                    self.goal_index = (self.goal_index + 1) % len(self.goals)
                    self.calculate_path()


    def calculate_path(self):
        if self.goal_index >= len(self.goals):
            self.goal_index = 0
        goal_node = self.goals[self.goal_index]
        self.path = self.graph.a_star(self.current_node, goal_node)
        if self.path:
            self.current_target = self.path.pop(0)

class MemoryRecord:
    time_last_sensed: int = 0
    time_became_visible: int = 0
    time_last_visible: int = 0
    last_sensed_position: pygame.Vector2 = pygame.Vector2(0, 0)
    is_within_fov: bool = False
    is_shootable: bool = False
    

class GoalThink:
    def __init__(self, owner):
        self.owner = owner
        self.subgoals = []

    def process(self):
        # Process subgoals and remove completed ones
        while self.subgoals and self.subgoals[0].is_complete():
            self.subgoals.pop(0)
        if self.subgoals:
            self.subgoals[0].process()

    def add_subgoal(self, goal):
        self.subgoals.insert(0, goal)

    def arbitrate(self):
        # Determine the most appropriate goal to pursue
        pass
    

class SensoryMemory:

    def __init__(self, owner, memory_span: float):
        self.owner = owner
        self.memory_map = defaultdict(MemoryRecord)
        self.memory_span = memory_span

    def make_new_record_if_not_already_present(self, bot):
        if bot not in self.memory_map:
            self.memory_map[bot] = MemoryRecord()

    def update_with_sound_source(self, noise_maker):
        self.make_new_record_if_not_already_present(noise_maker)
        record = self.memory_map[noise_maker]
        record.time_last_sensed = pygame.time.get_ticks()
        record.last_sensed_position = noise_maker.position
    
    def update_vision(self):
        bots = self.owner.get_visible_opponents()
        current_time = pygame.time.get_ticks()

        for bot in bots:
            self.make_new_record_if_not_already_present(bot)
            record = self.memory_map[bot]
            record.is_within_fov = True
            record.time_last_sensed = current_time
            record.time_became_visible = current_time
            record.last_sensed_position = bot.position

    def is_opponent_shootable(self, opponent) -> bool:
        self.make_new_record_if_not_already_present(opponent)
        return self.memory_map[opponent].is_shootable
    
    def is_opponent_within_fov(self, opponent) -> bool:
        self.make_new_record_if_not_already_present(opponent)
        return self.memory_map[opponent].is_within_fov
    
    def get_last_recorded_position_of_opponent(self, opponent) -> Optional[pygame.Vector2]:
        self.make_new_record_if_not_already_present(opponent)
        return self.memory_map[opponent].last_sensed_position

    def get_time_opponent_has_been_visible(self, opponent) -> float:
        self.make_new_record_if_not_already_present(opponent)
        return (pygame.time.get_ticks() - self.memory_map[opponent].time_became_visible) / 1000.0

    def get_time_since_last_sensed(self, opponent) -> float:
        self.make_new_record_if_not_already_present(opponent)
        return (pygame.time.get_ticks() - self.memory_map[opponent].time_last_sensed) / 1000.0

    def get_time_opponent_has_been_out_of_view(self, opponent) -> float:
        self.make_new_record_if_not_already_present(opponent)
        return (pygame.time.get_ticks() - self.memory_map[opponent].time_last_visible) / 1000.0

    def get_list_of_recently_sensed_opponents(self):
        bots = []
        current_time = pygame.time.get_ticks()
        for bot, record in self.memory_map.items():
            if (current_time - record.time_last_sensed) / 1000.0 <= self.memory_span:
                bots.append(bot)
        return bots


class TargetingSystem:
    def __init__(self, owner: RavenBot):
        self.owner = owner
        self.current_target = None

    def update(self):
        opponents = self.owner.sensory_memory.get_list_of_recently_sensed_opponents()
        if opponents:
            self.current_target = min(
                opponents,
                key=lambda bot: self.owner.position.distance_to(bot.position)
            )
        else:
            self.current_target = None

    def is_target_present(self) -> bool:
        return self.current_target is not None

    def is_target_within_fov(self) -> bool:
        return (
            self.current_target is not None
            and self.owner.sensory_memory.is_opponent_within_fov(self.current_target)
        )

    def is_target_shootable(self) -> bool:
        return (
            self.current_target is not None
            and self.owner.sensory_memory.is_opponent_shootable(self.current_target)
        )

    def get_last_recorded_position(self) -> pygame.Vector2:
        if self.current_target is None:
            raise ValueError("No target currently assigned")
        return self.owner.sensory_memory.get_last_recorded_position_of_opponent(self.current_target)

    def get_time_target_has_been_visible(self) -> float:
        if self.current_target is None:
            raise ValueError("No target currently assigned")
        return self.owner.sensory_memory.get_time_opponent_has_been_visible(self.current_target)

    def get_time_target_has_been_out_of_view(self) -> float:
        if self.current_target is None:
            raise ValueError("No target currently assigned")
        return self.owner.sensory_memory.get_time_opponent_has_been_out_of_view(self.current_target)

    def get_target(self):
        return self.current_target

    def clear_target(self):
        self.current_target = None


class Weapon:
    def __init__(self, owner, ammo, projectile_speed, damage):
        self.owner = owner
        self.ammo = ammo
        self.projectile_speed = projectile_speed
        self.damage = damage

    def shoot_at(self, target_position):
        if self.ammo > 0:
            self.ammo -= 1
            print(f"Firing at {target_position} with {self.__class__.__name__}")
        else:
            print("Out of ammo!")

    def add_ammo(self, amount=10):
        self.ammo += amount
        print(f"Ammo refilled. Current ammo: {self.ammo}")

    def evaluate_situation(self, target_position):
        distance = self.owner.position.distance_to(target_position)
        return self.damage / (distance + 1)  # Example heuristic
