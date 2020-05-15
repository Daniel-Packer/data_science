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
		move_dict["to"] = [(current_move.to_square % 8), (current_move.to_square // 8)  ]
		move_dict["from"] = [(current_move.from_square % 8) , (current_move.from_square // 8)  ]
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
		major_minor_piece_count = len(gameDict['white_pieces'][move_counter]['N']) +len(gameDict['white_pieces'][move_counter]['B'])+len(gameDict['white_pieces'][move_counter]['R'])+len(gameDict['white_pieces'][move_counter]['Q']) +len(gameDict['black_pieces'][move_counter]['N'])+ len(gameDict['black_pieces'][move_counter]['R']) + len(gameDict['black_pieces'][move_counter]['B']) + len(gameDict['black_pieces'][move_counter]['Q'])
		if not gameDict['middle_game_index']:
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
		if not (gameDict['end_game_index'])  and major_minor_piece_count <= 6:
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

### is_guarded function

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


## Outputs a list [A,B,C,D,A#,B#,C#,D#,E#,side] where
## A,B,C,D : one-hots for ECO codes (omit E)
## A#,B#,C#,D#,E# : interaction terms, the one-hot times the number of the opening
## side : Float in [-1,1] i.e. Queen to King for white's preferred development side
##       Measures this by finding the center of mass at the start of the midgame, or 0 if midgame is not reached
def white_development(game_dict):
    # I'll include a one-hot for E at first, remove it later
    output = np.zeros(11)
    
    # Opening info from the dict
    letter = game_dict['opening'][0]
    number = int(game_dict['opening'][1:])
    
    # Set one-hots
    output[ord(letter.upper())-65] = 1
    
    # Set interaction terms
    for i in range(5):
        output[i+5] = output[i] * number
    
    # Remove the one-hot for E
    output = np.delete(output,4)
    
    # Calculate the center of mass on the midgame turn
    index = game_dict['middle_game_index']
    if index:
        # Midgame was reached
        piece_dict = game_dict['white_pieces'][index]
        piece_locations_array = list(piece_dict.values())
        piece_x_locations = [coord[0] for sublist in piece_locations_array for coord in sublist]
        output[-1] = (np.mean(piece_x_locations) - 3.5) / 3.5
    
    return output

## Outputs a list [earliness, side, side_relative, artificial, development] where
## earliness : float in [0,1], 1/(the turn they castled), 0 if no castle
## side : +1 for king side, -1 for queen side, 0 for no castle
## side_relative : +1 for same side as opponent, -1 for opposite side, 0 if one of them didn't castle
## artificial : 0 if bonafide castle, 1 if artificial
## development : float in [0,1] for how empty the back rank opposite their castling side is
##               calculated as 1 - (# pieces there) / 3, 0 if no castling
## So if white castles and they developed their queen side N and B but the R is still there, then development = 0.66

def white_castling(game_dict):
    
    # Call helper function to check who castled, which side, and when
    index_white, side_white, artificial_white = castle_index(game_dict,True)
    index_black, side_black, artificial_black = castle_index(game_dict,False)
    
    # Set the earliness
    if index_white:
        earliness = 1 / index_white
    else:
        earliness = 0
        
    # Set the relative side
    side_relative = side_white * side_black
    
    # Set the development
    if side_white == 0: # No castle
        development = 0
    elif side_white == 1: # King side castle, count number of pieces in a1,b1,c1
        piece_count = 0
        print('counting')
        # For x indices 0, 1, 2
        for i in range(3):
            # Check if there is a piece in square (i,0) at the time of the castle
            if game_dict['board_states'][index_white][i][0]:
                piece_count = piece_count + 1
        development = 1- piece_count / 3
    else: # Queen side castle, count number of pieces in f1,g1,h1
        piece_count = 0
        # For x indices 5, 6, 7
        for i in range(5,8):
            # Check if there is a piece in square (i,0) at the time of the castle
            if game_dict['board_states'][index_white][i][0]:
                piece_count = piece_count + 1
        development = 1 - piece_count / 3
        
    return (earliness, side_white, side_relative, artificial_white, development)

## Helper function to find castles
## Pass it the game_dict and a boolean for which player to check: True = white, False = black
##
## Returns (index, side, artificial):
## index : index of the board position of castling, None if no castle
## side : +1 for king side, -1 for queen side, 0 for neither
## artificial : 1 if the castle was artificial, 0 otherwise
##
## An artificial castle will be:
## - Any time through the mid game
## - King not on the d/e files
## - King on the back rank
## - King to the left/right of all its rooks
##
def castle_index(game_dict,player):
    
    # Find out if they did a real castle, which side, and which turn
    castled = False
    if player:
        key = 'white_moves'
    else:
        key = 'black_moves'
    for move in game_dict[key]:
        if move['special'] == 'O-O':
            # King side
            castled = True
            side = 1
            index = move['move_number']
        elif move['special'] == 'O-O-O':
            # Queen side
            castled = True
            side = -1
            index = move['move_number']
        if castled:
            return index, side, 0
    
    # If we got here, we didn't do a real castle. So, check for artificial castling:            
    # We'll look for artificial castling up to the end game, or the whole game if we never reach the end game
    # Get the locations of their pieces the turns they move
    if game_dict['end_game_index']:
        # If we got to the end game
        max_index = game_dict['end_game_index']
        if player:
            pieces = game_dict['white_pieces'][:max_index:2]
        else:
            pieces = game_dict['black_pieces'][1:max_index:2]
    else:
        # If we didn't get to the end game
        if player:
            pieces = game_dict['white_pieces'][::2]
        else:
            pieces = game_dict['black_pieces'][1::2]

    # Specifically, the king and rooks
    king_positions = [move['K'] for move in pieces]
    rook_positions = [move['R'] for move in pieces]

    # Loop over these positions to find the index of the castle
    index = None
    for i in range(len(king_positions)):
        king_pos = king_positions[i][0]

        # If we're still on the d/e files, keep searching
        if (king_pos[0] == 4) | (king_pos[0] == 3): continue
            
        # If we're not on our starting rank, keep searching
        if player & (king_pos[1] != 0): continue
        elif (not player) & (king_pos[1] != 7): continue

        # Check if I am to the right or left of all my rooks:
        # Right (for each rook, check if we're to the right of its x index; then see if this is true for all rooks)
        if all([(rook_pos[0] < king_pos[0]) for rook_pos in rook_positions[i]]):
            index = i
            side = 1 # King side castle
            break
        # Left
        elif all([(rook_pos[0] > king_pos[0]) for rook_pos in rook_positions[i]]):
            index = i
            side = -1 # Queen side castle
            break
    # Note that when we set index = i this indexes white/black's moves, not the board positions
    
    # If we artificial castled, return that
    if index:
        index = game_dict[key][i]['move_number']
        return index, side, 1
    # Otherwise, no castle of any sort
    else:
        return None, 0, 0      

### discovered_checks function
### INPUT: takes in a game dict
### OUTPUT: dictionary of the following data
### discovered_checks_set_up : an integer corresponding the number of times the white player
### 	set up a discovered check
### discovered_checks_chances : an integer corresponding to the number of turns the white 
### 	player could give a discovered check 
### discovered_checks_given : int of moves in which  a player gives a discovered check 
###
### A discovered check is defined to be when white moves a piece, giving a check on the 
### black king with another piece

def discovered_checks(gameDict):
	discovered_checks_set_up = 0
	discovered_checks_chances = 0
	discovered_checks_given = 0

	#looks at where there was a discovered check given
	# goes through white moves and see where there was a check
	check_list = []
	for i in range(0, len(gameDict['white_moves'])):
		if gameDict['white_moves'][i]['check'] != '':
			check_list.append(i)
	
	# goes through the list of checks and sees if the check was a discovered check
	for i in check_list:	
		#loads board_state_FEN corresponding to after the move
		fen = gameDict["board_states_FEN"][2*i]
		board = chess.Board(fen)
		
		#gets list of attackers on the black king
		attackers = board.attackers(chess.WHITE, board.king(chess.BLACK))
	
		#checks if there is an attacker that is not the piece moved
		move_square = chess.square(gameDict['white_moves'][i]['to'][0], gameDict['white_moves'][i]['to'][1])
		if move_square in attackers: attackers.remove(move_square)
		if len(attackers) > 0:
			discovered_checks_given  += 1
			print("d check give: ", i)

	#goes through to see list of where a discovered check could be given
	for i in range(1, len(gameDict['white_moves'])):
		# create board state before white's move
		board = chess.Board(gameDict['board_states_FEN'][2*i -1])
		check_chance_flag = 0	

		for move in board.legal_moves:
			if board.gives_check(move):
				board1 = board.copy()
				board1.push(move)
				
								
				#gets list of attackers on the black king
				attackers = board1.attackers(chess.WHITE, board1.king(chess.BLACK))
				#checks if there is an attacker that is not the piece moved
				move_square = 	move.to_square
				if move_square in attackers: attackers.remove(move_square)
				if len(attackers) > 0:
					check_chance_flag  = 1
		if check_chance_flag: print("d check chance: ", i)
		discovered_checks_chances += check_chance_flag

	# check where a discovered check is set up. We define this to be move where, if black
	# didn't move, there would be a discovered check chance, note this doesn't apply when
	# there is a check
	for i in range(1, len(gameDict['white_moves'])):
		#checks if the move didn't just give check
		if gameDict['white_moves'][i]['check'] == '':
	
			# get move for after  white's move and sets the move to white again
			fen1  = gameDict['board_states_FEN'][2*i]
			fen = fen1[: fen1.find(" b ") +1] + "w" + fen1[fen1.find(" b ") +2:]

			# creates board and checks if there is a discovered check possible
			board = chess.Board(fen)		
			check_chance_flag = 0	

			for move in board.legal_moves:
				if board.gives_check(move):
					board1 = board.copy()
					board1.push(move)
								
					#gets list of attackers on the black king
					attackers = board1.attackers(chess.WHITE, board1.king(chess.BLACK))
	
					#checks if there is an attacker that is not the piece moved
					move_square = move.to_square
					if move_square in attackers: 
						attackers.remove(move_square)
					if len(attackers) > 0:
						check_chance_flag  = 1
			if check_chance_flag: print("d check set ", i)
			discovered_checks_set_up += check_chance_flag

	return {'discovered_checks_set_up' : discovered_checks_set_up, 'discovered_checks_given' :discovered_checks_given, 'discovered_checks_chances' :discovered_checks_chances}


### distribution_piece_moves function
###
### Input: gameDict
### Output: dictionary with keys 'P', 'N', 'B', 'R', 'Q', 'K' with values of percentage of time that type of piece was moved

def distribution_piece_moves(gameDict):
	dict = {'P':0, 'N':0, 'B':0, 'R':0, 'Q':0, 'K':0}

	for i in range(0, len(gameDict['white_moves'])):
		piece = gameDict['white_moves'][i]['piece']
		if piece == 'O':
			dict['K'] +=1/len(gameDict['white_moves'])
			dict['R'] +=1/len(gameDict['white_moves'])
		else: dict[piece] +=1/len(gameDict['white_moves'])
	return dict

