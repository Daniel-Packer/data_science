# Redo: Buhmann, Nima_Junior, Wolverines1

import pandas as pd
import functions as f
import lichess.api

#leaders = ['Arnelos', 'EnglishLongbow', 'Dacii', 'K-Georgiev', 'vistagausta', 'may6enexttime', 'grizzlybear79', 'LazaroBruzon', 'BabaRamdev', 'ChermanTrawz', 'bushidonaruto', 'Bestinblitz', 'opperwezen', 'NathyGonzalez', 'Ernst_Gruenfeld', 'Federicov93', 'Chesser22', 'Brrrrrrrr', 'Hunni-7', 'IGMGataKamsky','Eduiturri','arturchix','NIndja64','Polyclinical', 'elcaseno', 'gsvc', 'pozvonochek', 'epistimonas', 'dalmatinac101', 'Samson_Ofubu', 'Sigma_Tauri', 'CrazySage', 'ultraking1', 'Tryhard00', 'RD4ever', 'Rakhmanov_Aleksandr', 'OpeningGeek', 'Drvitman', 'jsl', 'Last7Samurai', 'KasparovModeOn', 'MELND-777', 'S2Pac', 'Evgeny_Levin', 'Chepursias', 'Feokl1995', 'Kiborg1987', 'Yarebore', 'mutdpro', 'Arteler', 'sillyMASTER', 'recapture', 'A_Kukhmazov', 'Tayka', 'jitanu76', 'Abik02', 'GMVallejo', 'ChessWeeb', 'Stratersest', 'Grandelicious', 'DrunkGatineau', 'BartoszSocko', 'Inventing_Invention', 'KIBORG799', 'dmitrij_IM', 'AdriD', 'backrankissues', 'IVK88', 'justantan', 'GrazyHunter', 'Wolverines1', 'Shant7777777', 'Farrukh78', 'Nima_Junior', 'federovski', 'AbasovN', 'Dynamo37', 'VerdeNotte', 'CaptainJames25', 'Alexander_Donchenko', 'ElAsesinoFavorito', 'Brigello', 'GaMbit9285', 'darkghoul', 'Buhmann', 'Kelevra317', 'Amin_____tb', 'muisback', 'Alexandr_KhleBovich', 'lenochka18', 'GeorgMeier', 'IlSalvatore']
leaders = ['backrankissues', 'IVK88', 'justantan', 'GrazyHunter']
leaders.reverse()

### Beginning of list that I've done before getting an error
#['Konevlad', 'Liem_Chess', 'HansSchmidt', 'Zhigalko_Sergei', 'PUKLO', 'Benefactorr', 'MikeGScarn','E-Shaposhnikov']

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

