from FMS import FMSPriority
from random import uniform
from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

LEO_COUNT = 10

SHEEP_COUNT = 100

# Leopard
@deserialize
@dataclass
class LeopardConfig(Config):
    speed_wander: float = 10.0
    nat_death: float = (10000) ** -1
    rot_timer: int = 1000
    hunt_timer: int = 100
    hunt_speed: float = 3.0
    eat_timer: int = 3
    stealth: float = 0.3

    still_weight: float = 0.0001
    walk_weight: float = 0.001
    eat_weight: float = 0.4

class LeoAction():
    def __init__(self, config = LeopardConfig()):
        self.config = config
class WanderLeo():
    pass
class HuntLeo():
    pass
class DieLeo():
    pass
class EatLeo():
    pass
class DieLeo():
    pass
class Sheep(Agent):
    pass


class WanderLeo(LeoAction):
    def do(self, ag):
        ag.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * config.speed_wander * uniform(0, (1 - ag.E) ** 2)
        ag.E = ag.E - config.still_weight - config.walk_weight
        if ag.E < 0:
            ag.E = 0
        return

    def switch(self, ag):
        return

    def prob(self, ag):
        prey = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).first()
        ag.current_prey = prey
        hunt_p = [HuntLeo(), int(prey is not None) * 0.99]
        nat_death_p = [DieLeo(), max(config.nat_death, int(ag.E == 0))]
        wander_p = [WanderLeo(), 1.0]

        # print(nat_death_p)

        return [nat_death_p, hunt_p, wander_p]

class HuntLeo(LeoAction):

    def do(self, ag):
        prey_move = ag.current_prey.pos - ag.pos
        prey_move = prey_move.normalize() * config.hunt_speed
        ag.move = prey_dir
        ag.E -= config.still_weight + config.walk_weight

    def switch(self, ag):
        ag.hunt_timer = config.hunt_timer

    def prob(self, ag):
        nat_death_p = [DieLeo(), max(config.nat_death, ag.E == 0)]
        eat_p = [EatLeo(), int((agg.pos - agg.current_prey.pos).length() <= 5)]
        hunt_p = [HuntLeo(), ag.hunt_timer > 0]
        wander_p = [WanderLeo(), 1.0]

        return [nat_death_p, eat_p, hunt_p, wander_p]

class EatLeo(LeoAction):
    def do(self, ag):
        ag.move = 0
        ag.E += config.eat_gain / config.eat_timer
        ag.eat_timer -= 1

    def switch(self, ag):
        ag.eat_timer = config.eat_timer

    def prob(self, ag):
        nat_death_p = [DieLeo(), max(config.nat_death, ag.E == 0)]
        eat_p = [EatLeo(), ag.eat_timer == 0]
        wander_p = [WanderLeo(), 1]

        return [nat_death_p, eat_p, wander_p]

class DieLeo(LeoAction):
    def do(self, ag):
        ag.move = Vector2(0, 0)
        ag.death_timer -= 1
        if ag.death_timer == 0:
            ag.kill()
    
    def switch(self, ag):
        return
    
    def prob(self, ag):
        return [[DieLeo(), 1]]


class Leopard(Agent, FMSPriority):
    config = LeopardConfig()
    current_action = WanderLeo()
    E: float = 1.0

    eat_timer = config.eat_timer
    death_timer = config.rot_timer
    hunt_timer = config.hunt_timer
        
    current_prey = None

    def change_position(self):
        # print(self.E, self.current_action)
        # self.there_is_no_escape()
        self.do()
        self.pos += self.move

# Sheep
@deserialize
@dataclass
class SheepConfig(Config):
    speed_wander: float = 1.0
    nat_death: float = (10000) ** -1
    rot_timer: int = 1000
    run_timer: int = 100
    hunt_speed: float = 3.0
    run_speed: float = 4.0
    eat_timer: int = 3

    still_weight: float = 0.01
    walk_weight: float = 0.01
    eat_weight: float = 0.4

class SheepAction():
    def __init__(self, config = SheepConfig()):
        self.config = config

class WanderSheep():
    pass
class RunSheep():
    pass
class HuntSheep():
    pass
class EatSheep():
    pass
class DieSheep():
    pass
class Grass(Agent):
    pass


class WanderSheep(SheepAction):
    def do(self, ag):
        ag.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * config.speed_wander * uniform(0, (1 - ag.E) ** 2)
        ag.E = ag.E - config.still_weight - config.walk_weight
        if ag.E < 0:
            ag.E = 0
        return

    def switch(self, ag):
        return

    def prob(self, ag):
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        grass = ag.in_proximity_accuracy().without_distance().filter_kind(Grass).first()
        ag.current_prey = grass
        ag.current_hunter = hunter
        run_p = [RunSheep(), int(hunter is not None) * 0.99 * (1 - hunter.config.stealth)]
        hunt_p = [HuntSheep(), int(grass is not None) * 0.99]
        nat_death_p = [DieSheep(), max(config.nat_death, int(ag.E == 0))]
        wander_p = [WanderSheep(), 1.0]

        return [nat_death_p, run_p, hunt_p, wander_p]

class RunSheep(SheepAction):
    def do(self, ag):
        ag.move = (ag.current_hunter.pos - ag.pos).normalize() * (self.config.run_speed * (-1))

    def switch(self, ag):
        pass

    def prob(self, ag):
        nat_death_p = [DieSheep(), max(config.nat_death, ag.E == 0)]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), int(hunter is not None)]
        wander_p = [WanderSheep(), 1]

        return [nat_death_p, run_p, wander_p]

class HuntSheep(SheepAction):
    def do(self, ag):
        prey_move = ag.current_prey.pos - ag.pos
        prey_move = prey_move.normalize() * config.hunt_speed
        ag.move = prey_dir
        ag.E -= config.still_weight + config.walk_weight

    def switch(self, ag):
        ag.hunt_timer = config.hunt_timer

    def prob(self, ag):
        nat_death_p = [DieSheep(), max(config.nat_death, ag.E == 0)]
        eat_p = [EatSheep(), int((agg.pos - agg.current_prey.pos).length <= 5)]
        hunt_p = [HuntSheep(), ag.hunt_timer > 0]
        wander_p = [WanderSheep(), 1.0]

        return [nat_death_p, hunt_p, wander_p]

class EatSheep(SheepAction):
    def do(self, ag):
        ag.move = 0
        ag.E += config.eat_gain / config.eat_timer
        ag.eat_timer -= 1

    def switch(self, ag):
        ag.eat_timer = config.eat_timer

    def prob(self, ag):
        nat_death_p = [DieSheep(), max(config.nat_death, ag.E == 0)]
        eat_p = [EatSheep(), ag.eat_timer == 0]
        wander_p = [WanderSheep(), 1]

        return [nat_death_p, eat_p, wander_p]

class DieSheep(DieLeo):
    pass


class Sheep(Agent, FMSPriority):
    config = SheepConfig()
    current_action = WanderLeo()
    E: float = 1.0

    eat_timer = config.eat_timer
    death_timer = config.rot_timer
    run_timer = config.run_timer
        
    current_prey = None

    def change_position(self):
        self.do()
        self.pos += self.move

#Grass

class Grass(Agent):
    def change_position(self):
        pass

class FMSLive(Simulation):
    tmp: int

config = LeopardConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
(
    FMSLive(
        config
    )
    # .spawn_site("images/circle2.png", config.window.as_tuple()[0] / 4, config.window.as_tuple()[0] / 4)
    # .spawn_site("images/site1.png", config.window.as_tuple()[0] / 4 * 3, config.window.as_tuple()[0] / 4)
    .batch_spawn_agents(LEO_COUNT, Leopard, images=["images/red.png"])
    .batch_spawn_agents(SHEEP_COUNT, Sheep, images=['images/green.png'])
    .run()
)