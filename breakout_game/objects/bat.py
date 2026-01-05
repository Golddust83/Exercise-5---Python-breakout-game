from .sprite import Sprite
from ..config import BAT, SCREEN
from ..utils import clamp
import pygame


class Bat(Sprite):

    def __init__(self):

        self.rect = pygame.Rect(
            SCREEN.width // 2 - BAT.width // 2,
            SCREEN.height - BAT.y_offset_from_bottom,
            BAT.width,
            BAT.height
        )

    def update(self, keys):
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= BAT.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += BAT.speed

        self.rect.x = clamp(self.rect.x, 0, SCREEN.width - self.rect.width)