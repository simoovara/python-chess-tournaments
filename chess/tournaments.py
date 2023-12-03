import random
from copy import copy

import pandas as pd
import chess.pgn

from PIL import Image, ImageFilter, ImageOps, ImageFont, ImageDraw


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
        self.standings = {}
        self.name = ""

    def add_name(self, name):
        assert not self.started
        self.name = name

    def add_player(self, player: Player):
        assert not self.started
        self.players.append(player)

    def order_standings(self):  # REVIEW: needs testing
        standings = {player: [player.points, player.rating] for player in self.players}

        # calling dict() because sorted() turns it into list[tuple[key, value]]
        self.standings = dict(sorted(standings.items(), key=lambda item: (item[1][0], item[1][1]), reverse=True))

    def start(self):
        self.started = True
        self.order_standings()

    def end(self):
        self.render_standings()
        self.started = False

    @staticmethod
    def points_rating_diff(player1, player2):
        return [player2, abs(player1.points - player2.points), abs(player1.rating - player2.rating)]

    def generate_pairings(self):
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

            if closest is None:
                continue
            pairings[player1] = closest[0]

        pairings_match = []
        for player in list(pairings.keys()):
            white = random.choice([player, pairings[player]])
            black = player if white == pairings[player] else pairings[player]

            pairings_match.append(Match(white, black))

        if not pairings_match:
            self.end()

        return pairings_match

    # will be done with pandas dataframe
    # check out https://pypi.org/project/dataframe-image/
    def generate_standings(self):
        assert self.started
        self.order_standings()

        data = {player: [player.points, player.rating] for player in self.standings.keys()}
        standings_df = pd.DataFrame(data=data)

        row_names = {
            0: "points",
            1: "rating"
        }
        standings_df = standings_df.rename(index=row_names)

        standings_df = standings_df.transpose()
        return standings_df

    def render_standings(self):
        assert self.started
        self.order_standings()

        # DO NOT CHANGE PLEASE, THEY WORK.
        name_rect = (64, 48, 64 + 2432, 48 + 115)

        width = 608
        height = 115

        left = 60
        right = left + width
        upper = 343
        lower = upper + height

        height_limit = 1800
        starting_rect = (left, upper, right, lower)

        image = Image.open("templates/chess.png").convert()
        font = ImageFont.truetype("fonts/font.ttf", size=75)

        title_crop = image.crop(box=name_rect)
        draw_title = ImageDraw.Draw(title_crop)

        title = self.name + " Standings" if self.name else "Tournament Standings"
        title_width = 2432
        title_height = 115
        _, _, w, h = draw_title.textbbox((0, 0), title, font=font)

        draw_title.text(xy=((title_width - w) / 2, (title_height - h) / 2), text=title, font=font, fill="black", stroke_width=1,
                        stroke_fill="black", align="center")

        image.paste(title_crop, box=(name_rect[0], name_rect[1]))

        def create_crops(lst):
            res = []
            for item in lst:
                item = image.crop(box=item)
                item = item.filter(ImageFilter.GaussianBlur(radius=18))
                item = ImageOps.expand(item, border=7, fill="black")
                res.append(item)

            return res

        for i, player in enumerate(self.standings.keys()):
            pos = i + 1
            name = player.name
            points = player.points
            rating = player.rating

            # (left, upper, right, lower)
            second_rect = (starting_rect[2], upper, starting_rect[2] + width, lower)
            third_rect = (second_rect[2], upper, second_rect[2] + width, lower)
            fourth_rect = (third_rect[2], upper, third_rect[2] - 6 + width, lower)

            rects = [starting_rect, second_rect, third_rect, fourth_rect]
            crops = create_crops(rects)
            columns = [pos, name, points, rating]

            for rect, column, crop in zip(rects, columns, crops):
                crop_copy = copy(crop)
                draw = ImageDraw.Draw(crop_copy)
                _, _, w, h = draw.textbbox((0, 0), str(column), font=font)
                draw.text(((width - w) / 2, (height - h) / 2), str(column), font=font, fill="black", stroke_width=1,
                          stroke_fill="black")

                image.paste(crop_copy, box=(rect[0], rect[1]))

            upper = upper + height
            lower = upper + height
            if lower > height_limit:
                break
            starting_rect = (left, upper, right, lower)

        image.save("standings.png")

    def play_matches(self):
        assert self.started
        assert self.pairings
