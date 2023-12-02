from chess.tournaments import *

tournament = SwissTournament()

tournament.add_player(TournamentPlayer("John1", 1900))
tournament.add_player(TournamentPlayer("John2", 1600))
tournament.add_player(TournamentPlayer("John3", 1300))
tournament.add_player(TournamentPlayer("John4", 1000))
tournament.add_player(TournamentPlayer("John5", 700))
tournament.add_player(TournamentPlayer("John6", 400))
tournament.add_player(TournamentPlayer("John7", 100))
tournament.add_player(TournamentPlayer("John8", 1))

tournament.start()

round_1_pairings = tournament.generate_pairings()
for pair in round_1_pairings:
    pair.sim_play()

print(round_1_pairings)

round_2_pairings = tournament.generate_pairings()
print(round_2_pairings)
