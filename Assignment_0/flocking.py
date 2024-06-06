from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random


@deserialize
@dataclass
class FlockingConfig(Config):
    # You can change these for different starting weights
    alignment_weight: float = 1.0
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5
    maximum_vel: float = 20
    leader_birds = 10
    to_mouse = 1

    # These should be left as is.
    delta_time: float = 0.5                                   # To learn more https://gafferongames.com/post/integration_basics/ 
    mass: int = 20                                            

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


# class Bird(Agent):
#     config: FlockingConfig
    
#     def Alignment(self, birds, neighbours):
#         # neighbours = birds.count()
#         res = Vector2(0, 0)
#         if neighbours != 0:
#             # print('ALIGNMENT')
#             for i in birds:
#                 res += i.move
#             # res += self.config.leader_bird.move
#             res = res / neighbours
#             res -= self.move
#         return res
    
#     def Seperation(self, birds, neighbours):
#         res = Vector2(0, 0)
#         # neighbours = birds.count()
#         if neighbours != 0:
#             # print("SEPERATION", neighbours)
#             for i in birds:
#                 res += self.pos - i.pos
#             # res += self.pos - self.config.leader_bird.pos
#             res = res / neighbours
#         return res
    
#     def Cohesion(self, birds, neighbours):
#         # neighbours = birds.count()
#         if neighbours == 0:
#             return Vector2(0, 0)
#         # print("COHESION")
#         xn = Vector2(0, 0)
#         for i in birds:
#             xn += i.pos
#         # xn += self.config.leader_bird.pos
#         xn = xn / neighbours

#         fc = xn - self.pos
#         return fc - self.move
    
#     def RandomMovement(self):
#         minimum = 0
#         res = Vector2(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
#         res = res.normalize() * 20
#         return res

#     def f_total(self):
#         birds = self.in_proximity_performance()
#         count = birds.count()
#         birds = birds.collect_set()

#         #Add leader
#         # birds.add(self.config.leader_bird)
#         # count += 1

#         a = self.Alignment(birds, count)
#         s = self.Seperation(birds, count)
#         c = self.Cohesion(birds, count)

#         # print(c)

#         alpha, beta, gama = self.config.weights()

#         res = a * alpha + c * beta + s * gama
#         # if birds.count() == 0:
#         #     res = self.RandomMovement()
#         res = res / self.config.mass

#         return res
    
#     def maxVel(self, vel):
#         max_vel = self.config.maximum_vel
#         res = vel
#         if vel.length() >= max_vel:
#             res = vel.normalize() * max_vel
#         return res
        

#     def change_position(self):
#         # Pac-man-style teleport to the other end of the screen when trying to escape
#         self.there_is_no_escape()
        
#         #YOUR CODE HERE -----------

#         #With Leader
#         # if self.id == 0:
#         #     self.config.leader_bird = self
#         #     mouse_x, mouse_y = pg.mouse.get_pos()[:2]
#         #     bird_x, bird_y = self.pos.x, self.pos.y

#         #     self.move = Vector2(mouse_x - bird_x, mouse_y - bird_y)
#         #     self.pos += self.move
#         # else:
#         #     f_total = self.f_total()
#         #     move = self.move + f_total
#         #     move = self.maxVel(move)
#         #     self.move = move
#         #     self.pos += self.move * self.config.delta_time

#         #Without Leader
#         f_total = self.f_total()
#         move = self.move + f_total
#         move = self.maxVel(move)
#         self.move = move
#         self.pos += self.move * self.config.delta_time
        #END CODE -----------------

class Bird(Agent):
    config: FlockingConfig

    def Alignment(self, neighbours):
        count = len(neighbours)

        total_v = Vector2(0, 0)
        for boid in neighbours:
            total_v += boid.move
        avg_v = total_v / count
        return avg_v  - self.move
    
    def Cohesion(self, neighbours):
        count = len(neighbours)

        total_p = Vector2(0, 0)
        for boid in neighbours:
            total_p += boid.pos
        avg_p = total_p / count
        return avg_p - self.pos - self.move
    
    def Seperation(self, neighbours):
        count = len(neighbours)

        total_disp = Vector2(0, 0)
        for boid in neighbours:
            total_disp += boid.pos - self.pos
        avg_disp = total_disp / count
        return avg_disp
    
    def Force(self):
        neighbours = self.in_proximity_performance().collect_set()

        if len(neighbours) == 0:
            return Vector2(0, 0)

        a = self.Alignment(neighbours)
        s = self.Seperation(neighbours)
        c = self.Cohesion(neighbours)

        a_w, c_w, s_w = self.config.weights()

        total_force = a_w * a + s_w * s + c_w * c
        total_force = total_force / self.config.mass

        return total_force
    
    def maxVel(self):
        max_v = self.config.maximum_vel
        self.move = self.move.normalize() * max_v

    def movement_flock(self):
        self.move += self.Force()
        self.maxVel()

    def movement_pos(self, pos):
        move = pos - self.pos
        self.move += move.normalize() * self.config.to_mouse

    def position(self):
        self.pos += self.move * self.config.delta_time

    def change_position(self):
        self.there_is_no_escape()

        self.movement_flock()
        if self.id < self.config.leader_birds:
            self.movement_pos(Vector2(pg.mouse.get_pos()))
        self.position()



class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .run()
)
