from enum import Enum


class GameState(Enum):
    NON_EXISTENT = None

    WAITING = "WAITING"
    STARTED = "STARTED"
    ABORTED = "ABORTED"
    FINISHED = "FINISHED"
