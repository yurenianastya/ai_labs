import triggers


class RavenMap():

    def __init__(self, walls, trigger_sys, spawn_points, nav_graph):
        self.walls = walls
        # class for managing event triggers
        self.trigger_sys = triggers.TriggerSystem()
        self.spawn_points = spawn_points
        self.nav_graph = triggers.NavGraph()

    def render():
        pass

    def load_map(filename):
        return False
    
    def calc_travel_cost_between_nodes(node1, node2):
        pass

    def update_trigger_sys(bots):
        pass


class RavenWeapons():
    
    def __init__(self, type, fire_rate, owner, projectile_spd, ideal_range):
        self.type = type
        self.fire_rate = fire_rate
        self.owner = owner
        self.projectile_spd = projectile_spd
        self.ideal_range = ideal_range

    def aim_at(target):
        """
        this method aims the weapon at the given target by rotating the weapon's
        owner's facing direction (constrained by the bot's turning rate).
        It returns true if the weapon is directly facing the target.
        """
        return False
    
    def shoot_at(target):
        """
        this discharges a projectile from the weapon at the given target position
        (provided the weapon is ready to be discharged)
        """
        return 0
    
    def render():
        pass

    def get_desirability(dist_to_target):
        """
        this method returns a value representing the desirability of using the weapon.
        This is used by the AI to select the most suitable weapon for a bot's
        current situation. This value is calculated using fuzzy logic (chapter 10).
        """
        return 0
    
    def get_projectile_speed():
        return 0
    
    def num_rounds_remaining():
        return 0
    
    def decrement_num_rounds():
        return 0
    
    def increment_num_rounds():
        return 0
    
    def get_gun_type():
        return ''


class RavenBot():

    def __init__(self, base_hp, base_weapon):
        self.base_hp = base_hp
        self.base_weapon = 'blaster'


class RavenGame(): 

    def __init__(self, map, bots, selected_bot, projectiles):
        self.map = map
        self.bots = bots
        # the user may select a bot to control manually. This variable points which one
        self.selected_bot = selected_bot
        # this list contains any active projectiles 
        self.projectiles = projectiles

    def render():
        pass

    def update():
        pass
    
    def load_map(filename):
        """ loads an environment from a file """
        return False

    def is_path_obstructed(vec_a, vec_b, bounding_radius=0):
        """
        returns true if a bot of size BoundingRadius
        cannot move from A to B
        without bumping into world geometry
        """
        return False
    
    def get_all_bots_in_fov(bot):
        """
        returns a list of bots in the FOV of the given bot
        """
        return []
    
    def if_second_visible_to_first(first_bot, second_bot):
        """
        returns true if the second bot is unobstructed
        by walls and in the field of view of the first
        """
        return False