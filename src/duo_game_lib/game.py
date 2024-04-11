import time
from collections.abc import Callable
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Any

from entities.judge import Judge
from entities.move import Move, MoveMetadata
from entities.players.player import Player
from game_state import GameState


class Game(AbstractContextManager):
    def __init__(
        self,
        logger: Callable[[str], None],
        player1: Player,
        player2: Player,
        judge: Judge,
    ) -> None:
        self.__logger: Callable[[Any], None] = logger
        self.__players: list[Player] = [player1, player2]
        self.__judge: Judge = judge

    def __enter__(self) -> Any:
        for player in self.__players:
            player.__enter__()

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        for player in self.__players:
            player.__exit__(exc_type, exc_value, traceback)

    def play(self, turns: int = 250, debug: bool = False):
        """
        Starts a game and return result as dict.

        Args:
            turns (int, optional): The maximum amount of turns to play. Defaults to 250.
            debug(bool, optional): If True, prints debug info to console. Defaults to False.

        Returns:
            dict[str, Any]: The game result containing winner, moves, etc.
        """
        previous_move = ""
        state = GameState.CONTINUE
        move = None

        i = 0

        while state == GameState.CONTINUE:
            if i == turns:
                state = GameState.MAX_TURNS
                break

            player = self.__players[i % 2]
            move, elapsed_time = self.__play_one_move(player, previous_move)

            if elapsed_time >= 1000:
                state = GameState.TIMEOUT
                continue

            state = self.__judge.validate(move)

            if state == GameState.CONTINUE:
                self.__judge.add_move(move)
                state = self.__judge.is_game_over()

            move_object = Move(
                move,
                state,
                MoveMetadata(
                    elapsed_time,
                    self.__judge.analyze(),
                    player.get_and_reset_current_logs(),
                ),
            )
            self.__logger(move_object)

            previous_move = move

            if debug:
                self.__print_debug_info(move_object)

            i += 1

        self.__logger(f"END: {state}")

    def __play_one_move(self, player: Player, prev_move: str) -> tuple[str, int]:
        start_time = time.perf_counter()

        move = player.play(prev_move)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)

        return (move, elapsed_time)

    def __print_debug_info(self, move: Move) -> None:
        info = "\n".join(
            [
                self.__judge.get_debug_info(),
                str(move),
            ]
        )

        print(info)
