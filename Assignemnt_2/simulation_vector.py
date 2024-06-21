from vi import Simulation
from vi.config import Config
from typing import Optional
import pygame as pg
import threading

class SimulationWithVectors(Simulation):
    def after_update(self):
        # Call the parent class's after_update to handle the usual drawing
        self.draw_movement_vectors()
        super().after_update()


    def draw_movement_vectors(self):
        for agent in self._agents:
            agent: Agent  # type: ignore
            movement_vector = agent.move
            if movement_vector.length() > 0:
                self.draw_vector(agent.pos, movement_vector)

    def draw_vector(self, position, vector):
        start_pos = (int(position.x), int(position.y))
        end_pos = (int(position.x + vector.x * 10), int(position.y + vector.y * 10))  # Scale vector for visibility
        pg.draw.line(self._screen, (255, 0, 0), start_pos, end_pos, 2)  # Red color for vectors
