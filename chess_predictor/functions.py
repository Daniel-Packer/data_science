## Slider Imports
from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets

## General data science stuff
import numpy as np
import pandas as pd

## Need this to work with chess data
import chess.pgn
from lichess.format import SINGLE_PGN
import lichess.api

## Need this to save the test data
import json

########################################
### Getting data
########################################

# dict_list = json.load(open('Dan_blitz_games.json')) gets a list of game_dict's

## Imports games and converts them into the dictionary type that we want
def get_dicts(player_name, num_games, time_type, format_):
    games_raw = lichess.api.user_games(player_name, max=num_games, perfType=num_games, format = format_)
    games_list = games_raw.split('\n\n\n')
    return [get_gameDict(game) for game in games_list]

## This will generates a JSON of the test_data to be created of the games of a player, in the quantity given by num_games
def make_test_data(file_name, player_name, num_games, time_type):
    with open(file_name, 'w') as f:
        json.dump(get_dicts(player_name, num_games, time_type, SINGLE_PGN), f)

########################################
### Processing Data
########################################        


### The get_gameDict function reads in a lichess pgn string and returns a game dictionary

### The game dictionary is a dictionary formatted with the following keys:
### 'white_moves' : [list of move dictionaries for white moves (documentation below)]
### 'black_moves' : [list of move dictionaries for black moves]
### 'white_player' : string of the lichess username of the white player
### 'black_player' : string of the lichess username of the black player
### 'opening' : string of the ECO code of the opening
### 'time_control' : string of the time control "starting time (in seconds)+increment time
###									(in seconds)
### 'board_states' : list of board states 2d array of strings (documentation below)
### 'board_states_FEN' : list of FEN strings for the game states
### 'white_pieces': list (same length as 'board_states') of dicts of lists of tuples of piece locations that board state
###     ex. The first entry is {'P': [(rank,file),...], 'N': [...], ...}
### 'black_pieces': same as white_pieces, but for black's pieces
### middle_game_index: returns an int corresponding to the first half move of the mid-game. The middle game is defined to start when there are 10 or fewer minor/major pieces, or 
###	when the back rank of each player has four or fewer pieces. 
###	If the game is too short to reach mid-game, the index is None.
### end_game_index: returns an int corresponding to the first half move of the endgame. The end game is defined to start when there are 6 or fewer minor/major pieces on the board.
###	If the game is too short to reach endgame, the index in None.

### move dictionary
### the move dictionary has the following keys
### 'piece' : string of the piece moved (ex. 'P', 'R', 'N', 'B', 'K', 'Q', 'O' (castle))
### 'from' : tuple of integers of the starting square of the piece moved (1,8) corresponds to a8
### 'to' : tuple of integers of the ending square of the piece move
### 'capture' : string of the piece captured (returns empty string if no capture, strings are same as piece)
### 'move_number' : integer of the half move number (ex white's first move is 0, black's is 1)
### 'special' : returns a string giving the following game conditions: en passant = 'p', promotion = piece 
###			character, castle = "O-O" or "O-O-O"
### 'check' : returns a string corresponding to whether or not there is a check or checkmate check = "+",
###				checkmate  = '#', neither is given by empty string

### board_states
### 8x8 array of strings. board_state[file][rank] gives piece, uppercase for white, lowercase for black

def get_gameDict(gamepgn):
	#creates the game dictionary
	gameDict = {'white_moves' : [], 'black_moves' :[], 'board_states' :[], 'board_states_FEN' :[], 'white_pieces': [], 'black_pieces': [],'middle_game_index' : None, 'end_game_index' : None }
	
	#reads in white_player
	name_start = gamepgn.find('White "') +7
	name_end = gamepgn.find('"', name_start)
	gameDict["white_player"] = gamepgn[name_start :name_end]
	
	#reads in black_player
	name_start = gamepgn.find('Black "') +7
	name_end = gamepgn.find('"', name_start)
	gameDict["black_player"] = gamepgn[name_start :name_end]

	#reads in opening
	name_start = gamepgn.find('ECO') + 5
	name_end = gamepgn.find('"', name_start)
	gameDict["opening"] = gamepgn[name_start:name_end]
	
	#reads in time_control
	name_start = gamepgn.find('TimeControl') +13
	name_end = gamepgn.find('"', name_start)
	gameDict["time_control"] = gamepgn[name_start:name_end]

	### The following iterates strips the pgn to the moves only then iterates through
	### the moves and creates board states and move dictionary
	# strips pgn to moves
	end_header = gamepgn.rfind("]")
	move_begin = gamepgn.find('1.', end_header)
	moves  = gamepgn[move_begin:]
	move_list = moves.split()
	for move in move_list:
		 if move[0].isdigit(): move_list.remove(move)

	# runs through each move and creates the move dictionary and board states
	# creates a counter for half moves
	move_counter = 0

	# creates the FEN for the opening board and creates a chess board object for that
	# state
	current_board = chess.Board(chess.STARTING_FEN)
	
	#writes the first FEN
	#gameDict["board_states_FEN"].append(current_board.fen())

	for move in move_list:
		move_dict = {"move_number": move_counter, "capture" : '', "check" : '', "special": ''}
		#checks what piece was moved
		if move[0].isupper():
			move_dict["piece"] = move[0]
		else:
			move_dict["piece"] = "P"

		#parses the next move
		current_move = current_board.parse_san(move)

		#writes the to and from squares
		move_dict["to"] = [(current_move.to_square % 8) +1, (current_move.to_square // 8) +1 ]
		move_dict["from"] = [(current_move.from_square % 8) +1, (current_move.from_square // 8) +1 ]
		#checks if there was en passant
		if current_board.is_en_passant(current_move):
			move_dict["special"] = "p"
			move_dict["capture"] = "P"
		#if not checks if capture and of what kind
		elif current_board.is_capture(current_move):	
			captured_piece = current_board.remove_piece_at(current_move.to_square)
			current_board.set_piece_at(current_move.to_square, captured_piece)
			move_dict["capture"] = captured_piece.symbol().upper()		

		#checks if promotion and writes it
		if move.find("=") != -1:
			move_dict["special"] = move[move.find("=") + 1]

		#checks if castle and wrtes it
		if move.find("-") != -1:
			move_dict["special"] = move 
		
	
		#writes the move dict to game dict
		if move_counter % 2:
			gameDict["black_moves"].append(move_dict)
		else: 
			gameDict["white_moves"].append(move_dict) 

		#pushes the move and writes the new FEN
		current_board.push(current_move)
		gameDict["board_states_FEN"].append(current_board.fen())

		#writes the array state
		board_copy = current_board.copy()
		board_state =  [['' for i in range(0,8)] for j in range(0,8)]
		for rank in range(0,8):
			for column in range(0,8):
				piece = board_copy.remove_piece_at(chess.SQUARES[8*rank + column ])
				if piece: board_state[column][rank] = piece.symbol()

		gameDict['board_states'].append(board_state)
        
		white_pieces, black_pieces = get_piece_locations(board_state)
		gameDict['white_pieces'].append(white_pieces)
		gameDict['black_pieces'].append(black_pieces)

		#checks if midgame 
		#counts numbers of minor/major pieces
		major_minor_piece_count = len(gameDict['white_pieces'][move_counter]['N']) +len(gameDict['white_pieces'][move_counter]['B'])+len(gameDict['white_pieces'][move_counter]['R'])+len(gameDict['white_pieces'][move_counter]['Q']) +len(gameDict['black_pieces'][move_counter]['N'])+ len(gameDict['black_pieces'][move_counter]['R']) +len(gameDict['black_pieces'][move_counter]['Q'])         
		if gameDict['middle_game_index'] == None :
			#gets the number of pieces on the back ranks
			back_rank_pieces_white = 0
			back_rank_pieces_black = 0
			for pieces_list in [gameDict['white_pieces'][move_counter]['N'],	gameDict['white_pieces'][move_counter]['B'], gameDict['white_pieces'][move_counter]['R'], gameDict['white_pieces'][move_counter]['Q']]: 
				for piece in pieces_list:
					if piece[1] == 0: back_rank_pieces_white += 1
			for pieces_list in [gameDict['black_pieces'][move_counter]['N'],	gameDict['black_pieces'][move_counter]['B'], gameDict['black_pieces'][move_counter]['R'], gameDict['black_pieces'][move_counter]['Q']]: 
				for piece in pieces_list:
					if  piece[1] == 7: back_rank_pieces_black += 1


			#set the counter if major_minor_piece_count <= 10 or back_rank_pieces <= 3 for each of black and white
			if (major_minor_piece_count <= 10) or (back_rank_pieces_white <= 3 and back_rank_pieces_black <= 3): 
				gameDict['middle_game_index'] = move_counter
		
		#checks if endgame
		if gameDict['end_game_index'] == None and major_minor_piece_count <= 6:
			gameDict['end_game_index'] = move_counter
        
		#check is mate or checkmate
		if current_board.is_check(): move_dict["check"] = "+"
		elif current_board.is_checkmate(): move_dict["check"] = "#"
				
		move_counter += 1

	return gameDict  


## Helper function for the above
## Takes in a 2D array for a board state and returns (white_dict,black_dict)
## Each dictionary has keys corresponding to pieces, and the values of each key are a list of tuples of their locations
def get_piece_locations(board):
    white_dict = {'P':[],'N':[],'B':[],'R':[],'Q':[],'K':[]}
    black_dict = {'P':[],'N':[],'B':[],'R':[],'Q':[],'K':[]}
    for file in range(8):
        for rank in range(8):
            piece = board[file][rank]
            if piece == '':
                continue
            elif piece.isupper():
                # White
                white_dict[piece].append((file,rank))
            else:
                # Black
                black_dict[piece.upper()].append((file,rank))
    return white_dict, black_dict



########################################
### Testing
########################################

### Feature tester

## Helper function that gives the widget output
def board_move(FENs, i):
    print('Move:',i)
    return chess.Board(FENs[i])
    
## Input a game_dict and list of functions to calculate features
## Creates an interactive slider to scroll through the game, and prints the feature values
def feature_test(game_dict, feature_list):
    print('White Player:', game_dict['white_player'])
    print('Black Player:', game_dict['black_player'])
    ## Read out the FENs so we don't need to call the dictionary:
    FENs = game_dict['board_states_FEN']
    ## Produce the interactive widget...lambda stuff deals with the fact that board_move takes 2 inputs, not 1
    interact((lambda i : board_move(FENs,i)), i=widgets.IntSlider(min=0, max=len(FENs)-1, step=1, value=0))
    
    print('Features:')
    for feature in feature_list:
        print(feature.__name__,'->', feature(game_dict))

        
########################################
### Features helper functions
########################################
        
## Given a game_dict, finds indices for the turns where where white/black first had 2 minor pieces, or -1 if this never happens
## Returns a tuple of
## white_board_index : used to index board_states for the position where white first had 2 minor pieces
## black_board_index : same for black
## white_turn_index : used to index white's moves for the move that brought black down to 2 minor pieces
## black_turn_index : same for black bringing white down to 2

def two_minor_pieces_turns(game_dict):
    # Get the indices for board states
    white_board_index = -1
    black_board_index = -1
    
    # Iterate over board positions
    for i in range(len(game_dict['board_states'])):
        board_state = game_dict['board_states'][i]
        
        # Check where the pieces are
        white_pieces, black_pieces = get_piece_locations(board_state)
        
        # If a board index is still zero, see if we have 2 minor pieces
        if (white_board_index == -1) & (len(white_pieces['N']) + len(white_pieces['B']) == 2):
            white_board_index = i
        if (black_board_index == -1) & (len(black_pieces['N']) + len(black_pieces['B']) == 2):
            black_board_index = i
            
        # If both board indices are nonzero we can stop iterating
        if (white_board_index > -1) & (black_board_index > -1):
            break
    
    # Now convert the board indices to turn indices for black and white
    if black_board_index == -1:
        white_turn_index = -1
    else:
        # It indexes white's moves, so just divide the index by 2
        white_turn_index = int(black_board_index / 2)
        
    if white_board_index == -1:
        black_turn_index = -1
    else:
        # It indexes blacks's moves, so subtract 1 first since black's first move is board_state[1]
        black_turn_index = int((white_board_index - 1) / 2)
    
    return white_board_index, black_board_index, white_turn_index, black_turn_index


### INPUT: is_guarded reads in a tuple of integers [file, rank] corresponding to position in question and the FEN of the current board state
### OUTPUT: returns a list of tuples corresponding to the squares of the pieces guarding the piece

def is_guarded(p_sq, board_state_FEN):
	# converts FEN to only the board part of the FEN
	fen = board_state_FEN.split()[0]

	#creates a baseboard object in python chess
	board = chess.BaseBoard(fen)

	#converts the piece_square tuple to a chess.SQUARE
	sq = chess.square(p_sq[0],p_sq[1])

	#creates a list for the pieces to return
	guarding_pieces = []

	#iterates through list of white pieces guarding and stores them in the list
	for guarder_square in board.attackers(chess.WHITE, sq):
		guarding_pieces.append([chess.square_file(guarder_square), chess.square_rank(guarder_square)])	

	return guarding_pieces


        
########################################
### Features
########################################

