import pygame

from .sprite import Sprite
from ..config import BAT, SCREEN
from ..utils import clamp


class Bat(Sprite):

    def __init__(self):
        rect = pygame.Rect(
            SCREEN.width // 2 - BAT.width // 2,
            SCREEN.height - BAT.y_offset_from_bottom,
            BAT.width,
            BAT.height,
        )
        super().__init__(rect)

    def update(self, *, keys = None, **kwargs) -> None:

        if not keys:
            return

        if keys[pygame.K_LEFT]:
            self.rect.x -= BAT.speed

        if keys[pygame.K_RIGHT]:
            self.rect.x += BAT.speed

        self.rect.x = int(clamp(self.rect.x, 0, SCREEN.width - self.rect.width))

    def draw(self, surface: pygame.Surface, **kwargs) -> None:

        pygame.draw.rect(surface, (14, 237, 233), self.rect, border_radius = 10)