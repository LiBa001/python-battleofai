__title__ = 'battleofai'
__author__ = 'Linus Bartsch'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018 Linus Bartsch'
__version__ = '1.0.0a'


from .client import Client
from .game import Game
from .enums import GameState
from .game_types import Core
from .game_session import GameSession
from .config import Config
from . import http, abc, errors
import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
logger.addHandler(console)
