from typing import List

import pygame


def get_pygame_events() -> List:
    return pygame.event.get()
