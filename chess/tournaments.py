import random

import chess.pgn


class Player:
    def __init__(self, name: str, rating: int):
        self.name = name
        self.rating = rating

        self.matches = {}

    def __repr__(self):
        return self.name

    # TODO: maybe add the pgn of the match idk something like that
    def add_match(self, opponent, colour, result):
        self.matches[opponent] = [colour, result]


class Match:
    def __init__(self, white: Player, black: Player):
        self.white = white
        self.black = black

        self.result = None

    def __repr__(self):
        base = f"{self.white} (White) VS {self.black} (Black): "
        if not self.result:
            return base + "Ongoing"
        return base + self.result

    def update_result(self, result: str):
        # result will be 1-0, 0-1 or 1/2-1/2
        self.result = result

    def sim_play(self):  # test function
        self.result = random.choice(["1-0", "0-1", "1/2-1/2"])
        self.add_match_to_players()

    def add_match_to_players(self):
        if self.result == "1-0":
            self.white.add_match(self.black, True, "1-0")
            self.black.add_match(self.white, False, "0-1")

        elif self.result == "1/2-1/2":
            self.white.add_match(self.black, True, "1/2-1/2")
            self.black.add_match(self.white, False, "1/2-1/2")

        else:
            self.white.add_match(self.black, True, "0-1")
            self.black.add_match(self.white, False, "1-0")


class TournamentPlayer(Player):
    def __init__(self, name, rating):
        super().__init__(name, rating)

        self.points = 0

    def add_match(self, opponent, colour, result):
        self.matches[opponent] = [colour, result]
        if result == "1-0":
            self.points += 1

        elif result == "1/2-1/2":
            self.points += .5


class BaseTournament:
    def __init__(self):
        self.players = []

        self.standings = {}
        self.started = False

    def start(self):
        self.started = True


class SwissTournament(BaseTournament):
    def __init__(self):
        super().__init__()

        self.pairings = {}

    def add_player(self, player: Player):
        self.players.append(player)

    def start_standings(self):  # REVIEW: needs testing
        standings = {player: player.rating for player in self.players}

        # calling dict() because sorted() turns it into list[tuple[key, value]]
        self.standings = dict(sorted(standings.items(), key=lambda item: item[1], reverse=True))

    def start(self):
        self.started = True
        self.start_standings()

    @staticmethod
    def points_rating_diff(player1, player2):
        return [player2, abs(player1.points - player2.points), abs(player1.rating - player2.rating)]

    def generate_pairings(self):  # TODO: need better (and more efficient) way to calculate pairings
        pairings = {}

        # standings - by definition - already have to be sorted by (in this case) rating and total points
        previous_matches = self.standings
        players = [player for player in self.standings]

        # REVIEW: needs testing
        for i, player1 in enumerate(previous_matches):
            closest = None

            if player1 in list(pairings.keys()) + list(pairings.values()):
                continue

            for player2 in players[i + 1:]:
                if player2 in list(pairings.keys()) + list(pairings.values()):
                    continue

                if player2 in list(player1.matches.keys()):
                    continue

                diff = self.points_rating_diff(player1, player2)

                if not closest:
                    closest = diff
                    continue

                if diff[1] < closest[1]:
                    closest = diff
                    continue

                if diff[2] < closest[2]:
                    closest = diff
                    continue
            pairings[player1] = closest[0]

        pairings_match = []
        for player in list(pairings.keys()):
            white = random.choice([player, pairings[player]])
            black = player if white == pairings[player] else pairings[player]

            pairings_match.append(Match(white, black))
        return pairings_match

    # check out https://pypi.org/project/datasheets/
    # might have to change function name
    def render_standings(self):
        assert self.started  # TODO: continue

    def play_matches(self):
        assert self.started
        assert self.pairings
