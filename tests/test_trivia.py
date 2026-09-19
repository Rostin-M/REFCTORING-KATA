"""
Tests de caracterizacion del juego de Trivia (trivia.py) ANTES del refactoring.

Objetivo: fijar el comportamiento observable actual (incluyendo defectos y
particularidades que se descubren al probar) para poder refactorizar con una
red de seguridad. No se corrige ningun comportamiento aqui, solo se documenta
lo que el codigo realmente hace hoy.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from trivia import Game


class TestGameSetup:
    def test_new_game_has_no_players(self):
        game = Game()
        assert game.how_many_players == 0

    def test_is_playable_false_with_less_than_two_players(self):
        game = Game()
        game.add("Chet")
        assert game.is_playable() is False

    def test_is_playable_true_with_two_or_more_players(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        assert game.is_playable() is True


class TestAddPlayer:
    def test_add_player_appends_name_and_prints_confirmation(self, capsys):
        game = Game()
        result = game.add("Chet")

        assert result is True
        assert game.players == ["Chet"]

        out = capsys.readouterr().out
        assert "Chet was added" in out
        assert "They are player number 1" in out

    def test_add_first_player_initializes_state_one_index_ahead(self):
        # NOTA (defecto documentado): add() lee self.how_many_players
        # DESPUES de hacer append, asi que para el primer jugador
        # (how_many_players pasa a valer 1) inicializa places/purses/
        # in_penalty_box en el indice 1, no en el indice 0. El indice 0
        # queda con los valores por defecto de __init__ ([0]*6), que
        # coinciden por casualidad con los que se "querian" poner.
        game = Game()
        game.add("Chet")

        assert game.places[1] == 0
        assert game.purses[1] == 0
        assert game.in_penalty_box[1] is False
        # el indice 0 nunca fue tocado por add(), sigue en su valor inicial
        assert game.places[0] == 0
        assert game.in_penalty_box[0] == 0
        assert game.in_penalty_box[0] is not False  # es int 0, no bool False

    def test_how_many_players_reflects_count(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        assert game.how_many_players == 2

    def test_internal_players_list_stays_in_sync_with_names(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        assert [p.name for p in game._players] == ["Chet", "Pat"]
        assert all(p.place == 0 and p.purse == 0 and p.in_penalty_box is False for p in game._players)


class TestCurrentCategory:
    @pytest.mark.parametrize(
        "place,expected",
        [
            (0, "Pop"), (4, "Pop"), (8, "Pop"),
            (1, "Science"), (5, "Science"), (9, "Science"),
            (2, "Sports"), (6, "Sports"), (10, "Sports"),
            (3, "Rock"), (7, "Rock"), (11, "Rock"),
        ],
    )
    def test_category_by_place(self, place, expected):
        game = Game()
        game.add("Chet")
        game.places[0] = place
        assert game._current_category == expected


class TestAskQuestion:
    def test_ask_question_pop(self, capsys):
        game = Game()
        game.add("Chet")
        game.places[0] = 0
        game._ask_question()
        assert "Pop Question 0" in capsys.readouterr().out

    def test_ask_question_science(self, capsys):
        game = Game()
        game.add("Chet")
        game.places[0] = 1
        game._ask_question()
        assert "Science Question 0" in capsys.readouterr().out

    def test_ask_question_sports(self, capsys):
        game = Game()
        game.add("Chet")
        game.places[0] = 2
        game._ask_question()
        assert "Sports Question 0" in capsys.readouterr().out

    def test_ask_question_rock(self, capsys):
        game = Game()
        game.add("Chet")
        game.places[0] = 3
        game._ask_question()
        assert "Rock Question 0" in capsys.readouterr().out

    def test_ask_question_pops_from_the_deck_in_order(self, capsys):
        game = Game()
        game.add("Chet")
        game.places[0] = 0
        game._ask_question()
        game._ask_question()
        out = capsys.readouterr().out
        assert "Pop Question 0" in out
        assert "Pop Question 1" in out


class TestRoll:
    def test_roll_moves_player_and_prints_status(self, capsys):
        game = Game()
        game.add("Chet")
        game.add("Pat")

        game.roll(3)

        assert game.places[0] == 3
        out = capsys.readouterr().out
        assert "Chet is the current player" in out
        assert "They have rolled a 3" in out
        assert "Chet's new location is 3" in out
        assert "The category is Rock" in out

    def test_roll_wraps_position_past_eleven(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.places[0] = 10

        game.roll(3)

        assert game.places[0] == 1  # 10 + 3 = 13 -> 13 - 12 = 1

    def test_roll_in_penalty_box_with_odd_roll_gets_out_and_moves(self, capsys):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.in_penalty_box[0] = True

        game.roll(3)

        assert game.is_getting_out_of_penalty_box is True
        assert game.places[0] == 3
        out = capsys.readouterr().out
        assert "Chet is getting out of the penalty box" in out

    def test_roll_in_penalty_box_with_odd_roll_and_wrap(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.in_penalty_box[0] = True
        game.places[0] = 10

        game.roll(3)

        assert game.places[0] == 1  # 10 + 3 = 13 -> wraps to 1

    def test_roll_in_penalty_box_with_even_roll_stays_in(self, capsys):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.in_penalty_box[0] = True
        place_before = game.places[0]

        game.roll(4)

        assert game.is_getting_out_of_penalty_box is False
        assert game.places[0] == place_before
        out = capsys.readouterr().out
        assert "Chet is not getting out of the penalty box" in out


class TestWasCorrectlyAnswered:
    def test_correct_answer_not_in_penalty_box_awards_coin_and_advances_turn(self, capsys):
        game = Game()
        game.add("Chet")
        game.add("Pat")

        result = game.was_correctly_answered()

        assert result is True
        assert game.purses[0] == 1
        assert game.current_player == 1
        out = capsys.readouterr().out
        # NOTA: el typo original ("corrent") fue corregido a "correct" como
        # una correccion de defecto explicita, separada del refactoring puro
        # (ver docs/01-analisis-code-smells.md, seccion 9).
        assert "Answer was correct!!!!" in out
        assert "Chet now has 1 Gold Coins." in out

    def test_correct_answer_not_in_penalty_box_wraps_turn_to_first_player(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.current_player = 1

        game.was_correctly_answered()

        assert game.current_player == 0

    def test_correct_answer_returns_false_when_purse_reaches_six(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.purses[0] = 5

        result = game.was_correctly_answered()

        assert game.purses[0] == 6
        assert result is False

    def test_penalty_box_getting_out_correct_answer_awards_coin(self, capsys):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.in_penalty_box[0] = True
        game.is_getting_out_of_penalty_box = True

        result = game.was_correctly_answered()

        assert result is True
        assert game.purses[0] == 1
        assert game.current_player == 1
        out = capsys.readouterr().out
        assert "Answer was correct!!!!" in out

    def test_penalty_box_getting_out_correct_answer_wraps_turn(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.current_player = 1
        game.in_penalty_box[1] = True
        game.is_getting_out_of_penalty_box = True

        game.was_correctly_answered()

        assert game.current_player == 0

    def test_penalty_box_not_getting_out_skips_coin_but_advances_turn(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.in_penalty_box[0] = True
        game.is_getting_out_of_penalty_box = False

        result = game.was_correctly_answered()

        assert result is True
        assert game.purses[0] == 0
        assert game.current_player == 1

    def test_penalty_box_not_getting_out_wraps_turn(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.current_player = 1
        game.in_penalty_box[1] = True
        game.is_getting_out_of_penalty_box = False

        game.was_correctly_answered()

        assert game.current_player == 0


class TestWrongAnswer:
    def test_wrong_answer_sends_to_penalty_and_advances_turn(self, capsys):
        game = Game()
        game.add("Chet")
        game.add("Pat")

        result = game.wrong_answer()

        assert result is True
        assert game.in_penalty_box[0] is True
        assert game.current_player == 1
        out = capsys.readouterr().out
        assert "Question was incorrectly answered" in out
        assert "Chet was sent to the penalty box" in out

    def test_wrong_answer_wraps_turn_to_first_player(self):
        game = Game()
        game.add("Chet")
        game.add("Pat")
        game.current_player = 1

        game.wrong_answer()

        assert game.current_player == 0
