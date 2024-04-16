from unittest import TestCase
from unittest.mock import Mock, call

from duo_game_lib.game import Game
from duo_game_lib.game_state import GameState


class TestGame(TestCase):
    def setUp(self) -> None:
        self.io_mock = Mock()
        self.player1_mock = Mock()
        self.player2_mock = Mock()
        self.judge_mock = Mock()
        self.game = Game(
            self.io_mock, self.player1_mock, self.player2_mock, self.judge_mock
        )

        self.player1_mock.get_and_reset_current_logs.return_value = "player1 logs"
        self.player2_mock.get_and_reset_current_logs.return_value = "player2 logs"
        self.judge_mock.analyze.return_value = 100

    def test_play_continue_continues_game(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2, 3]
        self.judge_mock.validate.return_value = GameState.CONTINUE
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(6)

        self.assertEqual(self.player1_mock.play.call_count, 3)
        self.assertEqual(self.player2_mock.play.call_count, 3)
        self.assertEqual(self.judge_mock.validate.call_count, 6)

    def test_play_lose_ends_game(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2, 3]
        self.judge_mock.validate.side_effect = [GameState.CONTINUE, GameState.LOSE]
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(6)

        self.assertEqual(self.player1_mock.play.call_count, 1)
        self.assertEqual(self.player2_mock.play.call_count, 1)
        self.assertEqual(self.judge_mock.validate.call_count, 2)

    def test_play_draw_ends_game(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2, 3]
        self.judge_mock.validate.return_value = GameState.CONTINUE
        self.judge_mock.is_game_over.side_effect = [GameState.CONTINUE, GameState.DRAW]

        self.game.play(6)

        self.assertEqual(self.player1_mock.play.call_count, 1)
        self.assertEqual(self.player2_mock.play.call_count, 1)
        self.assertEqual(self.judge_mock.validate.call_count, 2)
        self.assertEqual(self.judge_mock.is_game_over.call_count, 2)

    def test_play_illegal_ends_game(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2, 3]
        self.judge_mock.validate.side_effect = [GameState.CONTINUE, GameState.ILLEGAL]
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(6)

        self.assertEqual(self.player1_mock.play.call_count, 1)
        self.assertEqual(self.player2_mock.play.call_count, 1)
        self.assertEqual(self.judge_mock.validate.call_count, 2)

    def test_play_invalid_ends_game(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2, 3]
        self.judge_mock.validate.side_effect = [GameState.CONTINUE, GameState.INVALID]
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE
        self.game.play(6)

        self.assertEqual(self.player1_mock.play.call_count, 1)
        self.assertEqual(self.player2_mock.play.call_count, 1)
        self.assertEqual(self.judge_mock.validate.call_count, 2)
        self.assertEqual(self.judge_mock.is_game_over.call_count, 1)

    def test_validate_called_with_correct_moves(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2]
        self.judge_mock.validate.return_value = GameState.CONTINUE
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(5)

        self.judge_mock.validate.assert_has_calls(
            [call("a"), call(1), call("b"), call(2), call("c")]
        )

    def test_player_called_with_previous_moves(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2]
        self.judge_mock.validate.return_value = GameState.CONTINUE
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(5)

        self.player1_mock.play.assert_has_calls([call(1), call(2)])
        self.player2_mock.play.assert_has_calls([call("a"), call("b")])

    def test_play_logs_correct_moves(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2]
        self.judge_mock.validate.return_value = GameState.CONTINUE
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(5)

        calls = self.io_mock.call_args_list
        lines = [call.args[0] for call in calls[:-1]]
        expected_moves = ["a", "1", "b", "2", "c"]

        for i, line in enumerate(lines):
            self.assertIn(expected_moves[i], line)

    def test_play_logs_correct_states(self):
        states = [GameState.CONTINUE] * 4
        states.append(GameState.ILLEGAL)

        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2]
        self.judge_mock.validate.side_effect = states
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(5)

        calls = self.io_mock.call_args_list
        lines = [call.args[0] for call in calls[:-1]]

        for i, line in enumerate(lines):
            self.assertIn(str(states[i]), line)

    def test_out_of_turns_gamestate_is_max_turns(self):
        self.player1_mock.play.side_effect = ["a", "b", "c"]
        self.player2_mock.play.side_effect = [1, 2, 3]
        self.judge_mock.validate.side_effect = [GameState.CONTINUE] * 5
        self.judge_mock.is_game_over.return_value = GameState.CONTINUE

        self.game.play(2)

        self.io_mock.assert_called_with(f"END: {GameState.MAX_TURNS}")
