from enum import Enum


class GameState(Enum):
    CONTINUE = "CONTINUE"
    WIN = "WIN"
    LOSE = "LOSE"
    DRAW = "DRAW"
    INVALID = "INVALID"
    ILLEGAL = "ILLEGAL"
    MAX_TURNS = "MAX_TURNS"
    TIMEOUT = "TIMEOUT"

    def __str__(self):
        return self.value
