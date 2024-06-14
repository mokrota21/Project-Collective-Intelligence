from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random
import json

COUNT = 500
STILL = 0
MAX_I = 0
ALL = []
CAME = 0
TIME = 0
INSIDE = [0, 0]
LEAVE = False
TOTAL = 0

@deserialize
@dataclass
class FMSConfig(Config):
    speed: float = 30.0
    p_join: float = 1.5
    p_leave: float = 1.3
    D: int = int(COUNT ** (1/2)) * 10

def wander(self):
    global CAME, INSIDE
    c_site = self.on_site_id()
    if c_site is not None and random.uniform(0, 1) < self.config.p_join * (1/2 + (INSIDE[c_site] + 1) / (2 * COUNT)):
        # print(self.id)
        CAME += 1
        self.current_site = c_site
        self.enter_site = Vector2(self.pos.x, self.pos.y)
        self.escape_site = None
        INSIDE[self.current_site] += 1
        self.current = "Join"
        return

    movement = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.speed
    self.move = movement
    self.pos += self.move
    
def join(self):
        global STILL
        if self.escape_site is not None:
            self.randomize_site()
            self.still_i = 0
            STILL += 1
            self.current = "Still"
            return

        self.move = self.move.normalize() * self.config.speed
        self.pos += self.move
        self.join_t += 1
        if not self.on_site():
            self.escape_site = self.pos - self.move

def still(self):
    global INSIDE, STILL, MAX_I, LEAVE
    leave = False
    if not LEAVE:
        self.still_i += 1
    else:
        self.still_i += self.config.D - 1 - MAX_I

    if self.still_i % self.config.D == 0:
        
        # print("LEAVING")
        self.still_i = 0
        leave = random.uniform(0.0, 1.0) < self.leave_prob()


    if leave:
        self.continue_movement()
        INSIDE[self.current_site] -= 1
        STILL -= 1
        self.current = "Leave"
        return
    
    # if STILL == COUNT:
    #     MAX_I = max(MAX_I, self.still_i % self.config.D)
    # if self.id == COUNT - 1 and STILL == COUNT:
    #     LEAVE = (STILL == COUNT)
        # print(LEAVE)

def leave(self):
    if self.join_t == 0:
        self.current = "Wander"
        return
    
    self.move = self.move.normalize() * self.config.speed
    self.pos += self.move
    self.join_t -= 1
    

class Cockroach(Agent):
    config: FMSConfig
    in_site: bool = False
    current_site = None
    l_site = None
    current = "Wander"
    functions = {"Wander": wander, "Join": join, "Still": still, "Leave": leave}
    join_t = 0
    still_i = 0
    enter_site = None
    escape_site = None

    def leave_prob(self):
        count = 1 - INSIDE[self.current_site] / COUNT
        if count == 0:
            return self.config.p_leave
        return ((count ** (2)) * self.config.p_leave)

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
        global TIME, ALL, CAME, TOTAL
        if self.id == 0:
            TIME += 1
            if TIME == self.config.D:
                TOTAL += 1
                ALL.append([CAME, INSIDE])
                CAME = 0
                TIME = 0
            
        self.there_is_no_escape()

        self.functions[self.current](self)
        # self.l_site = self.on_site_id()

        # self.move = Vector2(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]) - self.pos
        # self.pos += self.move
        # print(self.on_site_id())

        

class Selection(Enum):
    SPEED = auto()
    P_JOIN = auto()
    P_LEAVE = auto()

class FMSLive(Simulation):
    selection: Selection = Selection.SPEED
    config: FMSConfig

    def handle_event(self, by: float):
        if self.selection == Selection.SPEED:
            self.config.speed += by * 10
        elif self.selection == Selection.P_JOIN:
            self.config.p_join += by
        elif self.selection == Selection.P_LEAVE:
            self.config.p_leave += by
            
    def before_update(self):
        global LEAVE, INSIDE, COUNT
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.SPEED
                elif event.key == pg.K_2:
                    self.selection = Selection.P_JOIN
                elif event.key == pg.K_3:
                    self.selection = Selection.P_LEAVE
                elif event.key == pg.K_4:
                    LEAVE = True

        s, j, l = self.config.speed, self.config.p_join, self.config.p_leave
        print(f"SPEED: {s:.1f} - P_JOIN: {j:.1f} - P_LEAVE: {l:.1f}")
        print(INSIDE)
        if max(INSIDE[0], INSIDE[1]) >= COUNT * 0.99:
            self.stop()

step = 500
new_data = []
while COUNT <= 5000:
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
    new_data.append({'count': COUNT, 'time_in_D': TOTAL})
    COUNT += step
    STILL = 0
    MAX_I = 0
    ALL = []
    CAME = 0
    TIME = 0
    INSIDE = [0, 0]
    LEAVE = False
    TOTAL = 0

file_name = "experiment_sqrt.json"
try:
    with open(file_name, "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = []

data += new_data

with open(file_name, "w") as file:
    json.dump(data, file, indent=4)
