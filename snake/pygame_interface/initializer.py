import sys
from contextlib import contextmanager
from typing import Iterator

import pygame


@contextmanager
def initialize_pygame() -> Iterator[None]:
    # pylint: disable=E1101
    pygame.init()
    yield
    pygame.quit()
    sys.exit()
