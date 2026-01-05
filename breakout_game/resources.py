import os
import pygame


def safe_load_sound(path):

    try:
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    except pygame.error:
        pass
    return None


def safe_load_image(path):

    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
    except pygame.error:
        pass
    return None


def safe_load_background(path):
    
    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert()
    except pygame.error:
        pass
    return None


class Resources:
    """
    Simple cache so each asset load only once
    """
    def __init__(self):
        self._images = {}
        self._sounds = {}
        self._backgrounds = {}

    def image(self, path):
        if path not in self._images:
            self._images[path] = safe_load_image(path)
        return self._images[path]

    def sound(self, path):
        if path not in self._sounds:
            self._sounds[path] = safe_load_sound(path)
        return self._sounds[path]

    def background(self, path):
        if path not in self._backgrounds:
            self._backgrounds[path] = safe_load_background(path)
        return self._backgrounds[path]