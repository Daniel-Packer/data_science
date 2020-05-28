import pandas as pd
import functions as f
import lichess.api

leaders = ['Yarebore', 'mutdpro', 'Arteler', 'sillyMASTER', 'recapture', 'A_Kukhmazov', 'Tayka', 'jitanu76', 'Abik02', 'GMVallejo', 'ChessWeeb', 'Stratersest', 'Grandelicious', 'DrunkGatineau', 'BartoszSocko', 'Inventing_Invention', 'KIBORG799', 'dmitrij_IM', 'AdriD']
leaders.reverse()

# Type of games'
game_type = 'blitz'

# How many games to read for each of them
num_games = 1000

def get_white_dicts(player_name, num_games, time_type, format_):
    games_raw = lichess.api.user_games(player_name, max=num_games, perfType=time_type, color = 'white', format = format_)
    games_list = games_raw.split('\n\n\n')
    return [f.get_gameDict(game) for game in games_list]

for player in leaders:
    features = []
    print(player)
    for game_dict in get_white_dicts(player,num_games, game_type, f.SINGLE_PGN):
        if game_dict['middle_game_index']:
            game_feat = f.get_features(game_dict)
            features.append(game_feat)
    df = pd.DataFrame(features)
    df.to_csv('data\\'+str(player) +'.csv')

