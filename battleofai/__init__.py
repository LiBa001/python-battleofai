from .client import Client
from .game import Game, GameState
from .game_types import Core
import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)
logger.addHandler(console)
