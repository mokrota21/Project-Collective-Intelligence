from FMS import FMSPriority
from random import uniform, randrange
from enum import Enum, auto
from pygame.math import Vector2
from vi import Agent, HeadlessSimulation
from vi.config import Config, dataclass, deserialize
from math import cos, radians
import polars as pl
import matplotlib.pyplot as plt

TOTAL_CAP = 200
LEO_COUNT = 0
MAX_NUM = 10 ** 9
SHEEP_COUNT = 0

# Leopard
@deserialize
@dataclass
class FMSConfig(Config):
    direction_change: int = 100
    leo_speed_wander: float = 3.0
    leo_hunt_speed: float = 4.0
    sheep_speed_wander: float = 1.0
    sheep_hunt_speed: float = 2.0
    sheep_run_speed: float = 5.0
    sheep_acceleration: float = 0.01
    sheep_reproduce_chance: float = 1.0
    sheep_mating_radius: float = 40.0
    leo_vision_field: float = cos(radians(100))
    sheep_vision_field: float = cos(radians(180))
    sheep_action_weight: float = 0.5
    leopard_action_weight: float = 0.5
    sheep_a: float = 0.3
    sheep_c: float = 0.2
    sheep_s: float = 0.0
    leo_nat_death: float = (10000) ** -1 * 0
    leo_rot_timer: int = 1000
    leo_hunt_timer: int = 30
    leo_stealth: float = 0.01
    leo_eat_speed: float = 0.4  
    leo_reproduce_timer: int = 2000
    leo_reproduce_chance: float = 1.0
    leo_hunt_chance: float = 0.1
    leo_energy_gain: float = 1.5
    leo_still_weight: float = 0.001
    leo_walk_weight: float = 0.0001
    leo_hungry: float = 0.60
    sheep_hungry: float = 0.70
    leo_full: float = 0.95
    sheep_full: float = 0.95
    sheep_nat_death: float = (10000) ** -1
    sheep_reproduce_timer: int = 8
    sheep_rot_timer: int = 1000
    sheep_run_timer: int = 100
    sheep_eat_timer: int = 3
    sheep_still_weight: float = 0.0005
    sheep_walk_weight: float = 0.0
    sheep_eat_weight: float = 0.04
    sheep_reproduce_thresh: float = 0.3
    leopard_reproduce_thresh: float = 0.8
    grass_still_weight: float = 0.0
    join_t_max: int = 10
    duration: int = 7200  # Run simulation for 2 minutes (60 ticks per second * 120 seconds)

def leo_see_sheep(leo, sheep):
    v1 = leo.move
    v2 = sheep.pos - leo.pos
    if v1.length() == 0:
        return False
    leo_sheep_cos = v1.dot(v2) / v1.length() / v2.length()
    return leo_sheep_cos > leo.config.leo_vision_field

def sheep_see_leo(sheep, leo):
    v1 = sheep.move
    v2 = leo.pos - sheep.pos
    if v1.length() == 0:
        return False
    sheep_leo_cos = v1.dot(v2) / v1.length() / v2.length()
    return sheep_leo_cos > sheep.config.sheep_vision_field

class LeoAction():
    def __init__(self, config = FMSConfig()):
        self.config = config

class WanderLeo():
    pass
class HuntLeo():
    pass
class DieLeo():
    pass
class EatLeo():
    pass
class ReproduceLeo():
    pass
class Sheep(Agent):
    pass
class Leopard(Agent):
    pass
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
class ReproduceSheep():
    pass
class Grass(Agent):
    pass

def Cohesion(agent, neighbours):
    count = len(neighbours)
    if count == 0:
        return Vector2(0, 0)
    total_p = Vector2(0, 0)
    for boid in neighbours:
        total_p += boid.pos
    avg_p = total_p / count    
    res = avg_p - agent.pos
    return res

class WanderLeo(LeoAction):
    def do(self, ag):
        if ag.timer % self.config.direction_change == 0:
            neighbours = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).collect_set()
            ag.move = ((Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() + Cohesion(ag, neighbours))).normalize() * self.config.sheep_speed_wander * uniform(0, (1 - ag.E) ** 2)
        return

    def switch(self, ag):
        return

    def prob(self, ag):
        prey = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).filter(lambda sheep: type(sheep.current_action) == DieSheep).first()
        if prey is None:
            prey = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).filter(lambda sheep: leo_see_sheep(ag, sheep)).first()
        ag.current_prey = prey
        hunt_p = [HuntLeo(), 0]
        if prey is not None:
            hungry = ag.E < self.config.leo_hungry
            hunt_p = [HuntLeo(), int(hungry) * self.config.leo_hunt_chance]
        nat_death_p = [DieLeo(), self.config.leo_nat_death]
        wander_p = [WanderLeo(), 1.0]

        return [nat_death_p, hunt_p, wander_p]

class ReproduceLeo(LeoAction):
    def do(self, ag):
        ag.move = Vector2(0, 0) 
        ag.reproduce()
        ag.can_reproduce = False
        
    def switch(self, ag):
        if ag.reproduce_timer == 0:
            ag.reproduce_timer = self.config.leo_reproduce_timer
    
    def prob(self, ag):
        nat_death_p = [DieLeo(), self.config.leo_nat_death]
        wander_p = [WanderLeo(), 1 - config.sheep_reproduce_chance]
        return [nat_death_p, wander_p]

class HuntLeo(LeoAction):
    def do(self, ag):
        prey_move = ag.current_prey.pos - ag.pos
        prey_move = prey_move.normalize() * config.leo_hunt_speed
        ag.move = prey_move
        ag.leo_hunt_timer -= 1

    def switch(self, ag):
        ag.leo_hunt_timer = config.leo_hunt_timer

    def prob(self, ag):
        nat_death_p = [DieLeo(), self.config.leo_nat_death]
        eat_p = [EatLeo(), int((ag.pos - ag.current_prey.pos).length() <= 5)]
        hunt_p = [HuntLeo(), ag.leo_hunt_timer > 0]
        wander_p = [WanderLeo(), 1.0]

        return [nat_death_p, eat_p, hunt_p, wander_p]

class EatLeo(LeoAction):
    def do(self, ag: Leopard):
        ag.current_prey.current_action = DieSheep()
        ag.move = Vector2(0, 0)
        change_E = min(config.leo_eat_speed, ag.current_prey.E)
        ag.E = min(ag.E * config.leo_energy_gain + change_E, 1.0)
        ag.current_prey.E -= change_E

    def switch(self, ag):
        pass

    def prob(self, ag):
        global LEO_COUNT, SHEEP_COUNT, TOTAL_CAP
        full = ag.E > self.config.leo_full
        prey_nutritional = ag.current_prey is not None and ag.current_prey.E > 0
        nat_death_p = [DieLeo(), self.config.leo_nat_death]
        eat_p = [EatLeo(), int(prey_nutritional and not full)]
        wander_p = [WanderLeo(), 1]
        mate_p = [ReproduceLeo(), int(self.config.leo_reproduce_chance)] \
            if LEO_COUNT * 10 + SHEEP_COUNT < TOTAL_CAP and ag.E >= self.config.leopard_reproduce_thresh and ag.can_reproduce else [ReproduceLeo(), 0]
        return [nat_death_p, eat_p, mate_p, wander_p]

class DieLeo(LeoAction):
    def do(self, ag):
        ag.change_image(1)
        ag.move = Vector2(0, 0)
        ag.death_timer -= 1
        if ag.death_timer == 0:
            ag.kill()
    
    def switch(self, ag):
        return
    
    def prob(self, ag):
        return [[DieLeo(), 1]]

class Leopard(Agent, FMSPriority):
    config = FMSConfig()
    current_action = WanderLeo()
    E: float = uniform(0.8, 1.0)
    timer: int = 0

    death_timer = config.leo_rot_timer
    leo_hunt_timer = config.leo_hunt_timer
    reproduce_timer = config.leo_reproduce_timer
        
    current_prey = None
    can_reproduce = False

    def change_position(self):
        global MAX_NUM
        self.there_is_no_escape()
        self.do()
        self.pos += self.move
        self.E = self.E - self.config.leo_still_weight - self.config.leo_walk_weight * self.move.length()
        self.timer = (self.timer + 1) % MAX_NUM
        self.reproduce_timer = max(0, self.reproduce_timer - 1)
        self.can_reproduce = self.reproduce_timer == 0
        if self.E < 0:
            self.kill()

    def update(self):
        self.save_data("E", self.E)
        self.save_data("Type", "Leopard")

# Sheep

class SheepAction():
    def __init__(self, config = FMSConfig()):
        self.config = config

class JoinGrassSiteSheep(SheepAction):
    def do(self, ag):
        ag.join_timer -= 1
        move = ag.current_prey.pos - ag.pos
        if move.length() == 0:
            return
        ag.move = move.normalize() * self.config.sheep_run_speed

    def switch(self, ag):
        ag.join_timer = randrange(self.config.join_t_max // 2, self.config.join_t_max)
    
    def prob(self, ag):
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        join_p = [JoinGrassSiteSheep(), int(ag.join_timer > 0)]
        eat_p = [EatSheep(), 1]
        return [nat_death_p, run_p, join_p, eat_p]

def Alignment(agent, neighbours):
    count = len(neighbours)
    if count == 0:
        return Vector2(0, 0)
    total_v = Vector2(0, 0)
    for boid in neighbours:
        total_v += boid.move
    avg_v = total_v / count
    res = avg_v  - agent.move
    return res

def Separation(agent, neighbours):
    count = len(neighbours)
    if count == 0:
        return Vector2(0, 0)
    total_p = Vector2(0, 0)
    for boid in neighbours:
        total_p += agent.pos - boid.pos
    avg_p = total_p / count
    res = avg_p
    return res

def CalculateMove(agent, neighbours, a, c, s):
    res = Alignment(agent, neighbours) * a + Cohesion(agent, neighbours) * c + Separation(agent, neighbours) * s
    return res

class WanderSheep(SheepAction):
    def do(self, ag):
        global MAX_NUM
        if ag.timer % self.config.direction_change == 0:
            neighbours = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).collect_set()
            ag.move = ((Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() + CalculateMove(ag, neighbours, 0.3, 0.3, 0.4))).normalize() * self.config.sheep_speed_wander * uniform(0, (1 - ag.E) ** 2)
        return

    def switch(self, ag):
        return

    def prob(self, ag):
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).filter(lambda leo: sheep_see_leo(ag, leo)).first()
        grass = ag.in_proximity_accuracy().without_distance().filter_kind(Grass).first()
        ag.current_prey = grass
        ag.current_hunter = hunter
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        hunt_p = [JoinGrassSiteSheep(), int(ag.E < self.config.sheep_hungry) * int(grass is not None) * 0.99]
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        wander_p = [WanderSheep(), 1.0]
        return [nat_death_p, run_p, hunt_p, wander_p]

class RunSheep(SheepAction):
    def do(self, ag):
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        if hunter is not None:
            l = ag.move.length()
            if l == 0:
                ag.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * self.config.sheep_run_speed * 0.1
            else:
                ag.move = ag.move.normalize() * min(l + self.config.sheep_acceleration, self.config.sheep_run_speed)
        else:
            ag.run_timer -= 1

    def switch(self, ag):
        ag.run_timer = self.config.sheep_run_timer

    def prob(self, ag):
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        run_p = [RunSheep(), int(hunter is not None and ag.run_timer != 0)]
        wander_p = [WanderSheep(), 1]
        return [nat_death_p, run_p, wander_p]

class HuntSheep(SheepAction):
    def do(self, ag):
        prey_move = ag.current_prey.pos - ag.pos
        prey_move = prey_move.normalize() * config.sheep_hunt_speed
        ag.move = prey_move

    def switch(self, ag):
        pass

    def prob(self, ag):
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        eat_p = [EatSheep(), int((ag.pos - ag.current_prey.pos).length() <= 5)]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        hunt_p = [HuntSheep(), 1.0]
        wander_p = [WanderSheep(), 1.0]
        return [nat_death_p, run_p, eat_p, hunt_p, wander_p]

class EatSheep(SheepAction):
    def do(self, ag):
        ag.move = Vector2(0, 0)
        change_E = min(config.sheep_eat_weight, ag.current_prey.E)
        ag.E += change_E
        ag.current_prey.E -= change_E

    def switch(self, ag):
        pass

    def prob(self, ag):
        global SHEEP_COUNT, LEO_COUNT, TOTAL_CAP
        full = ag.E > self.config.sheep_full
        prey_nutritional = ag.current_prey is not None and ag.current_prey.E > 0
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        eat_p = [EatSheep(), int(not full and prey_nutritional)]
        wander_p = [WanderSheep(), 1]
        mate = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).first()
        ag.current_mate = mate
        mate_p = [ReproduceSheep(), int(self.config.sheep_reproduce_chance)] \
            if SHEEP_COUNT + 10 * LEO_COUNT < TOTAL_CAP and mate is not None and ag.E >= self.config.sheep_reproduce_thresh and ag.can_reproduce else [ReproduceSheep(), 0]
        return [nat_death_p, run_p, mate_p, eat_p, wander_p]

class DieSheep(DieLeo):
    def do(self, ag):
        ag.change_image(1)
        ag.move = Vector2(0, 0)
        ag.death_timer -= 1
        if ag.death_timer == 0:
            ag.kill()
    
    def switch(self, ag):
        return
    
    def prob(self, ag):
        return [[DieSheep(), 1]]

class ReproduceSheep(SheepAction):
    def do(self, ag):
        ag.move = Vector2(0, 0) 
        ag.reproduce()
        ag.can_reproduce = False
    
    def switch(self, ag):
        global SHEEP_COUNT
        if ag.reproduce_timer == 0:
            ag.reproduce_timer = self.config.sheep_reproduce_timer
    
    def prob(self, ag):
        if ag.current_mate is not None:
            nat_death_p = [DieSheep(), self.config.sheep_nat_death]
            run_p = [RunSheep(), 0]
            wander_p = [WanderSheep(), 1 - config.sheep_reproduce_chance]
            return [nat_death_p, run_p, wander_p]

class Sheep(Agent, FMSPriority):
    config = FMSConfig()
    current_action = WanderSheep()
    E: float = uniform(0.8, 1.0)
    timer: int = 0
    join_timer: int = randrange(config.join_t_max // 2, config.join_t_max)
    death_timer = config.sheep_rot_timer
    run_timer = config.sheep_run_timer
    reproduce_timer = config.sheep_reproduce_timer
    current_prey = None
    current_mate = None
    can_reproduce = False

    def __init__(self, *args, **kwargs):
        global SHEEP_COUNT
        SHEEP_COUNT += 1
        super().__init__(*args, **kwargs)
    
    def __del__(self):
        global SHEEP_COUNT
        SHEEP_COUNT -= 1

    def change_position(self): 
        global MAX_NUM       
        self.there_is_no_escape()
        self.do()
        self.pos += self.move
        self.E = self.E - self.config.sheep_still_weight - self.config.sheep_walk_weight * self.move.length()
        self.timer = (self.timer + 1) % MAX_NUM
        self.reproduce_timer = max(0, self.reproduce_timer - 1)
        self.can_reproduce = self.reproduce_timer == 0
        if self.E < 0:
            self.kill()

    def update(self):
        self.save_data("E", self.E)
        self.save_data("Type", "Sheep")

#Grass

class Grass(Agent):
    config: FMSConfig
    E: float = 40.0
    disp: float = 500.0

    def change_position(self):
        global SHEEP_COUNT
        self.there_is_no_escape()
        if self.E <= 0:
            self.E = 10.0
            self.move = Vector2(0, 0)
            self.pos += Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * self.disp

    def update(self):
        self.save_data("E", self.E)
        self.save_data("Type", "Grass")

class FMSHeadless(HeadlessSimulation):
    tmp: int

config = FMSConfig(
    image_rotation=True,
    movement_speed=1,
    radius=150,
    seed=1,
    duration=7200,  # Run simulation for 2 minutes (60 ticks per second * 120 seconds)
)

def run_simulation(config: FMSConfig) -> pl.DataFrame:
    return (
        FMSHeadless(
            config
        )
        .batch_spawn_agents(20, Grass, images=['images/green_circle.png'])
        .batch_spawn_agents(100, Sheep, images=['images/white.png', 'images/red.png'])
        .batch_spawn_agents(10, Leopard, images=["images/snowleopard.png", "images/red.png"])
        .run()
        .snapshots
    )

def plot_population_dynamics(df: pl.DataFrame):
    df = df.to_pandas()
    df['frame'] = df['frame'].astype(int)
    df['Type'] = df['Type'].astype(str)
    
    population_counts = df.groupby(['frame', 'Type']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(10, 6))
    plt.plot(population_counts.index, population_counts['Sheep'], label='Sheep')
    plt.plot(population_counts.index, population_counts['Leopard'], label='Leopard')
    plt.xlabel('Time (frames)')
    plt.ylabel('Population')
    plt.title('Predator-Prey Population Dynamics')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    df = run_simulation(config)
    plot_population_dynamics(df)