from abc import ABC, abstractmethod
import pygame


class Sprite(ABC):
    """
    Abstract superclass:
    Forces every game object to implement update() and draw().
    (polymorphism)
    """
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

    @abstractmethod

    def update(self, *args, **kwargs) -> None:
        pass

    @abstractmethod

    def draw(self, surface: pygame.Surface, *args, **kwargs) -> None:
        pass