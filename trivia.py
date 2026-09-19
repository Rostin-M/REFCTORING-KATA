#!/usr/bin/env python3
from typing import ClassVar


class Player:
    def __init__(self, name):
        self.name = name
        self.place = 0
        self.purse = 0
        self.in_penalty_box = False


class Game:
    _CATEGORIES: ClassVar[list[str]] = ['Pop', 'Science', 'Sports', 'Rock']

    def __init__(self):
        self.players = []
        self._players = []
        self.places = [0] * 6
        self.purses = [0] * 6
        self.in_penalty_box = [0] * 6

        self.pop_questions = []
        self.science_questions = []
        self.sports_questions = []
        self.rock_questions = []

        self.current_player = 0
        self.is_getting_out_of_penalty_box = False

        for i in range(50):
            self.pop_questions.append("Pop Question %s" % i)
            self.science_questions.append("Science Question %s" % i)
            self.sports_questions.append("Sports Question %s" % i)
            self.rock_questions.append(self.create_rock_question(i))

        self._question_decks = {
            'Pop': self.pop_questions,
            'Science': self.science_questions,
            'Sports': self.sports_questions,
            'Rock': self.rock_questions,
        }

    def create_rock_question(self, index):
        return "Rock Question %s" % index

    def is_playable(self):
        return self.how_many_players >= 2

    def add(self, player_name):
        self.players.append(player_name)
        self._players.append(Player(player_name))
        self.places[self.how_many_players] = 0
        self.purses[self.how_many_players] = 0
        self.in_penalty_box[self.how_many_players] = False

        print(player_name + " was added")
        print("They are player number %s" % len(self.players))

        return True

    @property
    def how_many_players(self):
        return len(self.players)

    @property
    def _current_player_obj(self):
        return self._players[self.current_player]

    def roll(self, roll):
        print("%s is the current player" % self.players[self.current_player])
        print("They have rolled a %s" % roll)

        if self._current_player_obj.in_penalty_box:
            if roll % 2 != 0:
                self.is_getting_out_of_penalty_box = True

                print("%s is getting out of the penalty box" % self.players[self.current_player])
                self._move_current_player_and_ask_question(roll)
            else:
                print("%s is not getting out of the penalty box" % self.players[self.current_player])
                self.is_getting_out_of_penalty_box = False
        else:
            self._move_current_player_and_ask_question(roll)

    def _move_current_player_and_ask_question(self, roll):
        self._current_player_obj.place = self._current_player_obj.place + roll
        if self._current_player_obj.place > 11:
            self._current_player_obj.place = self._current_player_obj.place - 12

        print(self.players[self.current_player] + \
                    '\'s new location is ' + \
                    str(self._current_player_obj.place))
        print("The category is %s" % self._current_category)
        self._ask_question()

    def _ask_question(self):
        print(self._question_decks[self._current_category].pop(0))

    @property
    def _current_category(self):
        return self._CATEGORIES[self._current_player_obj.place % 4]

    def was_correctly_answered(self):
        if self._current_player_obj.in_penalty_box:
            if self.is_getting_out_of_penalty_box:
                return self._award_coin_and_advance_turn('Answer was correct!!!!')
            else:
                self._advance_turn()
                return True
        else:
            return self._award_coin_and_advance_turn('Answer was correct!!!!')

    def _award_coin_and_advance_turn(self, message):
        print(message)
        self._current_player_obj.purse += 1
        print(self.players[self.current_player] + \
            ' now has ' + \
            str(self._current_player_obj.purse) + \
            ' Gold Coins.')

        winner = self._did_player_win()
        self._advance_turn()

        return winner

    def _advance_turn(self):
        self.current_player += 1
        if self.current_player == len(self.players): self.current_player = 0

    def wrong_answer(self):
        print('Question was incorrectly answered')
        print(self.players[self.current_player] + " was sent to the penalty box")
        self._current_player_obj.in_penalty_box = True

        self._advance_turn()
        return True

    def _did_player_win(self):
        return not (self._current_player_obj.purse == 6)


from random import randrange

if __name__ == '__main__':
    not_a_winner = False

    game = Game()

    game.add('Chet')
    game.add('Pat')
    game.add('Sue')

    while True:
        game.roll(randrange(5) + 1)

        if randrange(9) == 7:
            not_a_winner = game.wrong_answer()
        else:
            not_a_winner = game.was_correctly_answered()

        if not not_a_winner: break
