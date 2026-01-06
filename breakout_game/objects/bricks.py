import pygame
from .sprite import Sprite


class Brick(Sprite):

    def __init__(self, rect: pygame.Rect, hits_left: int = 1, points: int = 20, kind: str = "soft"):

        super().__init__(rect)
        self.hits_left = hits_left
        self.points = points
        self.kind = kind  # "soft", "hard", "power"

    def color(self) -> tuple[int, int, int]:

        if self.kind == "hard":
            return (67, 60, 200)
        if self.kind == "power":
            return (255, 180, 80) 
        return (169, 42, 189)  # soft
    
    def update(self, **kwargs) -> None:
        pass
    
    def draw(self, surface: pygame.Surface, **kwargs) -> None:
        
        pygame.draw.rect(surface, self.color(), self.rect, border_radius = 6)

        if self.kind == "hard" and self.hits_left > 1:
            inner = self.rect.inflate(-12, -12)
            pygame.draw.rect(surface, (255, 210, 170), inner, width = 2, border_radius = 6)

    def hit(self) -> bool:
        
        """
        Apply 1 hit. 
        Returns true if destroyed.
        """
        self.hits_left -= 1
        return self.hits_left <= 0