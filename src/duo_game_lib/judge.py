from abc import ABC, abstractmethod
from typing import Any

from game_state import GameState


class Judge(ABC):
    """
    An abstract class for validating moves and generating debug infos of a game.
    """

    @abstractmethod
    def is_game_over(self) -> GameState:
        """
        Returns corresponding ending state if game over, otherwise CONTINUE.

        Returns:
            GameState: State of game.
        """

    @abstractmethod
    def validate(self, move: str) -> GameState:
        """
        Validates a move, does not change internal states.

        Args:
            move (str): Move to be validated.

        Returns:
            GameState: An integer describing game state.
        """

    @abstractmethod
    def add_move(self, move: str) -> Any:
        """
        Adds a move and updates internal data structures based on game.

        Args:
            move (str): The move to be added.

        Returns:
            Any: Additional information of added more when needed.
        """

    @abstractmethod
    def get_debug_info(self) -> str:
        """
        Returns debug info such as visual board state, player advantages, etc.

        Returns:
            str: Debug info.
        """

    @abstractmethod
    def get_all_moves(self) -> list[str]:
        """
        Returns all moves as string, formatted based on game.

        Returns:
            list[str]: List of moves.
        """

    @abstractmethod
    def analyze(self) -> float | int:
        """
        Evaluation game situation.
        Depends on game and may need additional arguments to evaluate situation.

        Returns:
            float | int: Evaluation of game.
        """
