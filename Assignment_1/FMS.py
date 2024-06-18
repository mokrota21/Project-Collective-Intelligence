from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random

COUNT = 100
ALL = []
CAME = 0
TIME = 0
INSIDE = [0, 0]

@deserialize
@dataclass
class FMSConfig(Config):
    speed: float = 30.0
    p_join: float = 0.8
    p_leave: float = 0.4
    p_join_no_site: float = 1 / COUNT
    t_join_no_site: int = 0
    D: int = 100

def wander(self):
    global CAME, INSIDE
    if self.on_site_id() is not None and random.uniform(0, 1) < self.config.p_join:
        CAME += 1
        self.last_site = self.on_site_id()
        self.enter_site = Vector2(self.pos.x, self.pos.y)
        self.escape_site = None
        INSIDE[self.last_site] += 1
        self.current = "Join"
        return

    movement = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.speed
    self.move = movement
    self.pos += self.move
    
def join(self):
        if self.escape_site is not None:
            self.randomize_site()
            self.still_i = 0
            self.current = "Still"
            return

        self.move = self.move.normalize() * self.config.speed
        self.pos += self.move
        self.join_t += 1
        if not self.on_site():
            self.escape_site = self.pos - self.move

def still(self):
    global INSIDE
    leave = False
    if self.still_i % self.config.D == 0:
        leave = random.uniform(0.0, 1.0) < self.leave_prob()

    if leave:
        self.continue_movement()
        INSIDE[self.last_site] -= 1
        self.current = "Leave"
        return

def leave(self):
    if self.join_t == 0:
        self.current = "Wander"
        return
    
    self.move = self.move.normalize() * self.config.speed
    self.pos += self.move
    self.join_t -= 1

def wander_no_site(self):
    if random.uniform(0, 1) < self.prob_join_no_site():
        self.last_site = self.on_site_id()
        self.enter_site = Vector2(self.pos.x, self.pos.y)
        self.escape_site = None
        self.current = "Join"
        return

    movement = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.speed
    self.move = movement
    self.pos += self.move

def join_no_site(self):
        if self.join_t == self.config.t_join_no_site is not None:
            # self.randomize_site()
            self.still_i = 0
            self.current = "Still"
            return

        self.move = self.move.normalize() * self.config.speed
        self.pos += self.move
        self.join_t += 1

def still_no_site(self):
    leave = False
    if self.still_i % self.config.D == 0:
        leave = random.uniform(0.0, 1.0) < self.leave_prob_no_site()

    if leave:
        self.continue_movement()
        self.current = "Leave"
        self.join_t = 5
        return

def leave_no_site(self):
    if self.join_t == 0:
        self.current = "Wander"
        return
    
    self.move = self.move.normalize() * self.config.speed
    self.pos += self.move
    self.join_t -= 1
    

class Cockroach(Agent):
    config: FMSConfig
    in_site: bool = False
    last_site = None
    current = "Wander"
    functions_norm = {"Wander": wander, "Join": join, "Still": still, "Leave": leave}
    functions_no_site = {"Wander": wander_no_site, "Join": join_no_site, "Still": still_no_site, "Leave": leave_no_site}
    join_t = 0
    still_i = 0
    enter_site = None
    escape_site = None

    def prob_join_no_site(self):
        count = self.in_proximity_performance().count()
        if count != 0:
            return self.config.p_join_no_site * ((count) ** (1/2))
        return self.config.p_join_no_site

    def leave_prob(self):
        count = INSIDE[self.last_site]
        if count == 0:
            return self.config.p_leave
        return ((count ** (-2)) * self.config.p_leave)
    
    def leave_prob_no_site(self):
        count = self.in_proximity_performance().count()
        if count == 0:
            return self.config.p_leave
        return ((count ** (-2)) * self.config.p_leave)

    def randomize_site(self):
        pos_v = self.escape_site - self.enter_site
        rand_l = random.uniform(0, pos_v.length())
        # rand_l = pos_v.length() / 2
        if pos_v.length()  != 0:
            rand_vector = pos_v.normalize() * rand_l
            # print(rand_vector, self.enter_site)
            self.pos = self.enter_site + rand_vector
        self.freeze_movement()

    def change_position(self):
        global TIME, ALL, CAME
        if self.id == 0:
            TIME += 1
            if TIME == self.config.D:
                ALL.append([CAME, INSIDE])
                CAME = 0
                TIME = 0
            
        self.there_is_no_escape()

        self.functions_norm[self.current](self)

        # self.move = Vector2(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]) - self.pos
        # self.pos += self.move
        # print(self.on_site_id())

        

class Selection(Enum):
    SPEED = auto()
    COHESION = auto()
    SEPARATION = auto()

class FMSLive(Simulation):
    tmp: int

config = FMSConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
(
    FMSLive(
        config
    )
    .spawn_site("images/site1.png", config.window.as_tuple()[0] / 4, config.window.as_tuple()[0] / 4)
    .spawn_site("images/site1.png", config.window.as_tuple()[0] / 4 * 3, config.window.as_tuple()[0] / 4)
    .batch_spawn_agents(COUNT, Cockroach, images=["images/red.png"])
    .run()
)
print(INSIDE)
