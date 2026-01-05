import pygame
from .sprite import Sprite


class Brick(Sprite):

    def __init__(self, rect, hits_left = 1, points = 20, kind = "soft"):
        self.rect = rect
        self.hits_left = hits_left
        self.points = points
        self.kind = kind  # "soft", "hard", "power"

    def color(self):
        if self.kind == "hard":
            return (67, 60, 200)
        if self.kind == "power":
            return (255, 180, 80) 
        return (169, 42, 189)  # soft
    
    def draw(self, surface):
        
        pygame.draw.rect(surface, self.color(), self.rect, border_radius = 6)

        if self.kind == "hard" and self.hits_left > 1:
            inner = self.rect.inflate(-12, -12)
            pygame.draw.rect(surface, (255, 210, 170), inner, width = 2, border_radius = 6)

    def hit(self) -> tuple[bool, int]:

        """
        Apply 1 hit. 
        Returns:
        - destroyed (bool)
        - points_to_add (int)

        Current behaviour:
        - if destroyed: add self.points
        - else: add +20 (passed in as score_on_non_destroy_hit)
        """
        self.hits_left -= 1

        if self.hits_left <= 0:
            return True, self.points

        return False, 0