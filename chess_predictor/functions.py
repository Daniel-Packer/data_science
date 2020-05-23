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
### Gobal Variables
########################################
### Creates values for the pieces
PIECE_VALUES = {'P':1, 'N':3, 'B':3, 'R':5, 'Q':9, 'K' :1000}



########################################
### Getting data
########################################

# dict_list = json.load(open('Dan_blitz_games.json')) gets a list of game_dict's

## Imports games and converts them into the dictionary type that we want
def get_dicts(player_name, num_games, time_type, format_):
    games_raw = lichess.api.user_games(player_name, max=num_games, perfType=time_type, format = format_)
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
### 'game_id' : lichess game_url 
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

	# reads in url
	url_start = gamepgn.find('Site') +6
	url_end = gamepgn.find('"', url_start)
	gameDict['game_id'] = gamepgn[url_start: url_end]

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
		move_dict["to"] = [current_move.to_square % 8, current_move.to_square // 8]
		move_dict["from"] = [current_move.from_square % 8 , current_move.from_square // 8]
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
    print('Midgame:',game_dict['middle_game_index'])
    print('Endgame:',game_dict['end_game_index'])
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
### INPUT: reads in a tuple of integers [file, rank] corresponding to position in question and the FEN of the current board state
### OUTPUT: returns a list of tuples corresponding to the squares of the pieces guarding the piece
def is_guarded(p_sq, board_state_FEN):
	# converts FEN to only the board part of the FEN
	fen = board_state_FEN.split()[0]

	#creates a baseboard object in python chess
	board = chess.BaseBoard(fen)

	#converts the piece_square tuple to a chess.SQUARE
	sq = chess.square(p_sq[0],p_sq[1])

	#checks color of the piece
	color = board.piece_at(sq).color

	#creates a list for the pieces to return
	guarding_pieces = []

	#iterates through list of same colored pieces guarding and stores them in the list
	for guarder_square in board.attackers(color, sq):
		guarding_pieces.append([chess.square_file(guarder_square), chess.square_rank(guarder_square)])	

	return guarding_pieces

### is_pinned function
### 
### INPUT: takes tuple of integers [file, rank] corresponding to position and FEN of the board
### OUTPUT: boolean True if pinned
### EXCEPTIONS: if not a piece on the square, or if it isn't the piece's turn to move

def is_pinned(p_sq, board_state_FEN):
	is_pinned_flag = False

	#creates a baseboard object in python chess
	board = chess.Board(board_state_FEN)


	#converts the piece_square tuple to a chess.SQUARE
	sq = chess.square(p_sq[0],p_sq[1])
	
	#throws error if no piece at the place
	piece = board.piece_at(sq)
	if piece == None:
		raise Exception("no piece here")
	# looks at the piece on the square
	piece_type = piece.symbol().upper()
	color = board.piece_at(sq).color
	
	#checks if correct color to move
	if color != board.turn: raise Exception("not right turn to move")
	
	
	
	#checks	if pinned to king
	if board.is_pinned(color, sq): return True
      
	 
	#because not pinned, removing the piece is valid, so we will look at all the possible moves with the piece on the board, and then all the moves when the piece is off the board
	#change the color of the move
	board.turn = 1- color 
	moves_before = [ move for move in board.pseudo_legal_moves]
	count = 0 
	board1 = board.copy()
	board1.remove_piece_at(sq)
	moves_after = [move for move in board1.pseudo_legal_moves]

	# looks at the difference between the two sets
	for move in moves_before:
		if move in moves_after: moves_after.remove(move)

	# looks at all the captures
	for move in moves_after:
		if board1.is_capture(move) == False:
			moves_after.remove(move)

	for move in moves_after:
		if not board1.piece_at(move.to_square):
			break
		piece_attacked = board1.piece_at(move.to_square).symbol().upper()
		#calculates if material is higher
		if PIECE_VALUES[piece_attacked] > PIECE_VALUES[piece_type]: 
			p_sq = [chess.square_file(move.to_square), chess.square_rank(move.to_square)]
			if len(is_guarded(p_sq, board1.fen())) == 0 : return True
			if PIECE_VALUES[piece_attacked] > PIECE_VALUES[board1.piece_at(move.from_square).symbol().upper()]: return True

	return is_pinned_flag

	
### material(gameDict, move_number, chess.COLOR)
### input: gameDict, (half) move_number, boolean 1 for white material, 0 for black
### ouput: sum of piece values of color on that turn

def material(gameDict, move_number, color):
	if move_number >= len(gameDict['board_states']): raise Exception('move_number out of index')

	if color : color_name = 'white_pieces'
	else: color_name = 'black_pieces'

	material_sum = 0

	for piece in ['P', 'B', 'N', 'R', 'Q']:
		material_sum += PIECE_VALUES[piece] * len(gameDict[color_name][move_number][piece])

	return material_sum
	

### gives_fork 
### 
### input: piece square (in format [file, rank]) and FEN
### output: boolean: 1 if the piece gives a fork, and zero if not

def gives_fork(piece, fen):
	# creates board
	board = chess.Board(fen)

	# converts piece to square
	square = chess.square(piece[0], piece[1])

	# finds the piece on the square
	piece_type = board.piece_at(square).symbol().upper()
	color = board.piece_at(square).color

	# gets list of attacks from the square
	attack_squares = board.attacks(square)

	#creates a counter of pieces of greater value or unguarded the piece attacks
	attack_count = 0

	for sq in attack_squares:
		if board.piece_at(sq):
			#checks that piece attacked is of opposite color
			if color != board.piece_at(sq).color:
				# checks if greater value or unguarded and if so adds 1 
				if PIECE_VALUES[board.piece_at(sq).symbol().upper()] > PIECE_VALUES	[piece_type] or  len(is_guarded([chess.square_file(sq), chess.square_rank(sq)], fen))==0:
					attack_count +=1

	return attack_count > 1

## Helper function to return the index of halfway through the early game
## Input: game_dict
## Output: index for board_states
def mid_earlygame(game_dict):
    if game_dict['middle_game_index']:
        index = int(game_dict['middle_game_index'] / 2)
    else:
        index = int(len(game_dict['board_states']) / 2)
    return index

## Helper function to return the index of halfway through the midgame
## Same I/O as mid_earlygame
## If we didn't reach the midgame at all, returns None (so that list[:index] takes a slice to the end)
def mid_midgame(game_dict):
    if game_dict['end_game_index']:
        # If we got to the end game
        index = int((game_dict['middle_game_index'] + game_dict['end_game_index'])/2)
    elif game_dict['middle_game_index']:
        # If we got to the mid game but not the end game
        index = int((game_dict['middle_game_index'] + len(game_dict['board_states']))/2)
    else:
        # If we didn't get to the mid game
        index = None
    return index

## Helper function to cap an index at the last index of the game if it is None
def cap_index(i, game_dict):
    max_i = len(game_dict['board_states_FEN']) - 1
    if i == None:
        return max_i
    else:
        return i

## Helper function to find castles
## Pass it the game_dict and a boolean for which player to check: True = white, False = black
##
## Returns (index, side, artificial):
## index : index of the board position of castling, None if no castle
## side : +1 for king side, -1 for queen side, 0 for neither
## artificial : 1 if the castle was artificial, 0 otherwise
##
## An artificial castle will be:
## - Happened by half way through the mid game
##    - Since the king moving out of the back row to artificial castle could trigger the start of the mid game
## - King not on the d/e files
## - King on the back rank
## - King to the left/right of all its rooks
##
def castle_index(game_dict,player):
    
    # Find out if they did a real castle, which side, and which turn
    castled = False
    if player:
        moves_key = 'white_moves'
    else:
        moves_key = 'black_moves'
    for move in game_dict[moves_key]:
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
    
    # If we got here, we didn't do a real castle. So, check for artificial castling
    # First I'll get a list of the board positions at the end of our moves
    
    # If we're looking at white, our moves start at the 0th board state; at 1st for black
    if player:
        start_index = 0
        pieces_key = 'white_pieces'
    else:
        start_index = 1
        pieces_key = 'black_pieces'
    
    # Next figure out the index of halfway through the mid game, or some other time if we didn't reach end/mid game
    end_index = mid_midgame(game_dict)
    
    # Now we can get the board states at the end of our moves
    pieces = game_dict[pieces_key][start_index:end_index:2]
    
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
    # The 'move_number' below fixes that
    
    # If we artificial castled, return that
    if index:
        index = game_dict[moves_key][i]['move_number']
        return index, side, 1
    # Otherwise, no castle of any sort
    else:
        return None, 0, 0


### Helper function for recognizing pawn chains
### Input: list of the pawns (already skewed) and j for the diagonal offset
### Output: number of length >=3 pawn chains, and length of longest pawn chain
def chain_helper(skewed_pawns, j):
    files = [pawn[0] for pawn in skewed_pawns if pawn[1] == j]
    
    chain_length = 0
    prev_file = -1
    count = 0
    longest_chain = 0
    
    # For each file of pawns on this diagonal, check if it extends the previous pawn chain
    for i in files:
        if i == prev_file + 1:
            chain_length = chain_length + 1
            # Since it does extend the previous chain, check if we hit length 3 or beat the max
            if chain_length == 3:
                count = count + 1
            if chain_length > longest_chain:
                longest_chain = chain_length
        else:
            # Otherwise, we broke the chain so start a new one
            chain_length = 1
        
        # Regardless of what happend, set this so that we know what file we just added to the chain
        prev_file = i
    
    return count, longest_chain

## The following detects a knight outpost in a specific turn for a player inputted as either 'white' or 'black'
def detect_outpost(game_dict, turn, player):
    board = game_dict['board_states'][turn]
    outpost_counter = 0 ## This value should never exceed 2, unless someone promotes to a knight and already has 2 on the board.
    if (player == 'white'):
        foe = 'black'
    else:
        foe = 'white'
    for knight in game_dict[player+'_pieces'][turn]['N']:
        potential_attackers = 0
        if (player == 'white'):
            ## We only consider it an 'outpost' if it's on the opponents side of the board:
            if (knight[1] < 4):
                break
            for pawn in game_dict[foe+ '_pieces'][turn]['P']:
                ## Checks if the pawn is in a file adjacent to the knight far enough back that it may attack the knight
                if ((abs(pawn[0] - knight[0]) == 1) and (pawn[1] > knight[1])):
                    potential_attackers += 1
            ## If there are no potential pawn attackers, we call the knight 'an outpost'
            if (potential_attackers == 0):
                outpost_counter += 1

        if (player == 'black'):
            ## We only consider it an 'outpost' if it's on the opponents side of the board:
            if (knight[1] > 3):
                break
            for pawn in game_dict[foe+ '_pieces'][turn]['P']:
                ## Checks if the pawn is in a file adjacent to the knight far enough back that it may attack the knight
                if ((abs(pawn[0] - knight[0]) == 1) and (pawn[1] < knight[1])):
                    potential_attackers += 1
            ## If there are no potential pawn attackers, we call the knight 'an outpost'
            if (potential_attackers == 0):
                outpost_counter += 1
    return outpost_counter
        
########################################
### Features
########################################

### Knight Features function, will return a dictionary of the form [Knight pair, knight outposts, knight repositioning, number of squares controlled].
def knight_features(game_dict):
    ## I try to do my best to only consider the player generally, so that if we later want to implement this for the black player too, we simply change player to be an input
    player = 'white'
    ## Initalize the features to be returned:
    knight_pair = 0
    knight_outpost_turns = 0
    knight_repo_counter = 0
    knight_attack_counter = 0
    num_knights = 0


    ## Check whether when there are only two minor pieces in play, those pieces are knights.

    if (two_minor_pieces_turns(game_dict)[0] > 0):
        if ((len(game_dict['white_pieces'][two_minor_pieces_turns(game_dict)[0]]['N']) == 2) and (two_minor_pieces_turns(game_dict)[0] != -1)):
            knight_pair = 1
    
    ## The following will iterate through midgame turns to check each board state for various features:
    # First check that we make it to the middle game:
    end_game_index = 0 ## This line shouldn't be necessary, just here in case we somehow get to the second if without hitting the first
    if (game_dict['end_game_index'] == None):
        end_game_index = int(len(game_dict['board_states']) - 1)
        ## In case the game ends before the endgame, this sets the endgame to be the last move in the game.
    else:
        end_game_index = game_dict['end_game_index']

    if (not (game_dict['middle_game_index'] == None)):
        for turn in range(int(game_dict['middle_game_index']/2), int(end_game_index/2)):
        ## turn iterates over white's moves ( game_dict['white_moves'] ) particularly, so to get the associated board states, we multiply turn by 2
            white_half_turn = turn*2 + 1
            num_knights = len(game_dict['white_pieces'][white_half_turn]['N'])
            ## The knight outpost code has been shunted off to the detect_outpost code below:
            knight_outpost_turns += detect_outpost(game_dict, white_half_turn, player)

            ## The following counts the knight repositioning
            if (game_dict[player+'_moves'][turn]['piece'] == 'N'): 
                ## the above checks if the player moved a knight this turn, then:
                for move in game_dict[player+'_moves']:
                    ## sums over all other knight moves in the game, scaling by distance
                    if ((move['piece'] == 'N') and (move['move_number']/2 != turn)):
                        knight_repo_counter += 1 / abs(move['move_number']/2 - turn)

            ## Now, we count the number of squares attacked by the knights at a given turn:
            # We get the FEN for white: (remove the +1 to get the FEN for black)
            board = chess.Board(game_dict['board_states_FEN'][white_half_turn])
            # We then check every legal move to see if the piece that can be moved is a knight, if so, we add one to the move counter. To change this to work for black, we need to make the 'N' lowercase or apply .toUpper() both so that we don't need the strings to match case
            for move in board.legal_moves:
                if (str(board.piece_at(move.from_square)).upper() == 'N'):
                    knight_attack_counter += 1 / num_knights
    
        ## Scale the repositioning, attack, and outpost counters by the total number of moves in the mid-game, so longer mid-games don't get overbiased.
        if (end_game_index - game_dict['middle_game_index'] > 0):
            knight_outpost_turns = knight_outpost_turns / (end_game_index - game_dict['middle_game_index'])

            knight_repo_counter = knight_repo_counter / (end_game_index - game_dict['middle_game_index'])
            knight_attack_counter = knight_attack_counter / (end_game_index - game_dict['middle_game_index']) 

    result_dict = {'wn_pair' : knight_pair, 'wn_outpost' : knight_outpost_turns, 'wn_repositioning': knight_repo_counter, 'wn_mobility' : knight_attack_counter}
    return result_dict

## Bishop Features are:
# Bishop Pair (1 for yes, 0 for no)
# King side Fianchetto
# Queen side Fianchetto
# Number of Squares controlled (sum/turns) of controlled squares by bishops in the middle game
# Opp color bishop (1 if yes, -1 if no, 0 if there is never one bishop for each player)
# Bishop_pawns: once white has only one bishop, adds +1 for each pawn on the opposite color, -1 for each on the same color of the opponents. Averages over number of turns that white has only one bishop
# Taking long diagonals (number of midgame turns in which a bishop is on a long diagonal/total number of midgame turns.


def bishop_features(game_dict):
    ## I try to do my best to only consider the player generally, so that if we later want to implement this for the black player too, we simply change player to be an input
    player = 'white'
    ## Initalize the features to be returned:
    bishop_pair = 0
    k_side_fianchetto = 0
    q_side_fianchetto = 0
    bishop_attack_counter = 0
    bishop_pawns = 0
    one_bishop_turn_counter = 0
    opp_color = 0
    long_diag_turns = 0
    long_diag_squares = [0, 9, 18, 27, 36, 45, 54, 63, 7, 14, 21, 28, 35, 42, 49, 56]
    
    ## Check whether when there are only two minor pieces in play, those pieces are bishops.
    if (two_minor_pieces_turns(game_dict)[0] > 0):
        if ((len(game_dict['white_pieces'][two_minor_pieces_turns(game_dict)[0]]['B']) == 2) and (two_minor_pieces_turns(game_dict)[0] != -1)):
            bishop_pair = 1

    ## The following method takes advantage of the fact that the sum of squares mod 2 returns the color of the square.
    for i in range(len(game_dict['board_states'])):
        # Get the board state:
        board_state = game_dict['board_states'][i]
        
        # Get the pieces
        white_pieces, black_pieces = get_piece_locations(board_state)

        # Check: we haven't already set opp_color, and both players each have one bishop
        if ((opp_color == 0) and ((len(white_pieces['B']) == 1) and (len(black_pieces['B']) == 1))):
            # Check if square parities match
            if ( (sum(white_pieces['B'][0]) % 2) == (sum(black_pieces['B'][0]) % 2)):
                opp_color = -1
            else:
                opp_color = 1
        # Add for coherent pawns, subtract for incoherent pawns 
        if (len(white_pieces['B']) == 1):
            one_bishop_turn_counter += 1
            white_parity = sum(white_pieces['B'][0]) % 2
            for j in range(len(black_pieces['P'])):
                if (sum(black_pieces['P'][j]) % 2 == white_parity):
                    bishop_pawns += -1
                else:
                    bishop_pawns += 1
    if (one_bishop_turn_counter != 0):
        # If the players ever had one bishop, normalize by number of turns when they had one bishop
        bishop_pawns = bishop_pawns / one_bishop_turn_counter


    ## The following will iterate through game turns to check each board state for various features (which may be present in various parts of the game):
    # First check that we make it to the middle game:
    if (game_dict['end_game_index'] == None):
        end_game_index = int(len(game_dict['board_states']) - 1)
        ## In case the game ends before the endgame, this sets the endgame to be the last move in the game. Otherwise, the end_game_index is what it should be
    else:
        end_game_index = game_dict['end_game_index']

    if (not (game_dict['middle_game_index'] == None)):
        ## Early game features tested here:
        for turn in range(int(game_dict['middle_game_index']/2)):
            white_half_turn = turn * 2
            
            board = chess.Board(game_dict['board_states_FEN'][white_half_turn])
            ## Check for fianchettos
            if (str(board.piece_at(9)).upper() == 'B'):
                k_side_fianchetto = 1
            if (str(board.piece_at(14)).upper() == 'B'):
                q_side_fianchetto = 1


        ## Middle game features tested here:
        for turn in range(int(game_dict['middle_game_index']/2), int(end_game_index/2)):
        ## turn iterates over white's moves ( game_dict['white_moves'] ) particularly, so to get the associated board states, we multiply turn by 2
            white_half_turn = turn*2 + 1
            num_bishops = len(game_dict['white_pieces'][white_half_turn]['B'])

            ## Now, we count the number of squares attacked by the bishop at a given turn:
            # We get the FEN for white: (remove the +1 to get the FEN for black)
            board = chess.Board(game_dict['board_states_FEN'][white_half_turn])
            # We then check every legal move to see if the piece that can be moved is a bishop, if so, we add one to the move counter. To change this to work for black, we need to make the 'N' lowercase or apply .upper() both so that we don't need the strings to match case
            for move in board.legal_moves:
                if (str(board.piece_at(move.from_square)).upper() == 'B'):
                    bishop_attack_counter += 1 / num_bishops

            for square in long_diag_squares:
                if (str(board.piece_at(square)) == 'B'):
                    long_diag_turns += 1/num_bishops
        ## Scale the attack and long_diag counters by the total number of moves in the mid-game, so longer mid-games don't get overbiased.
        if (end_game_index - game_dict['middle_game_index'] > 0):
            bishop_attack_counter = bishop_attack_counter / abs(end_game_index - game_dict['middle_game_index'])
            long_diag_turns = 2 * long_diag_turns / abs(end_game_index - game_dict['middle_game_index'])
            ## The 2 * is so that a score of one would be all bishops on their long diagonals for the entire midgame, since we are dividing by the total number of half-turns, while the counted turns are only those of white
    return_dict = {'wb_pair' : bishop_pair, 'wk_side_fianchetto' : k_side_fianchetto, 'wq_side_fianchetto' : q_side_fianchetto, 'wb_mobility' : bishop_attack_counter, 'wlong_diagonal_control' : long_diag_turns, 'wopposite_color_b': opp_color, 'b_p_coherency' : bishop_pawns}

    return return_dict


## Returns floats,
# nb_pref -- The preference in minor piece trades, favoring knights is positive, bishops is negative
# nb_develop -- The preference in which minor pieces are developed first, favoring knights is positive, bishops is negative

def minor_features(game_dict):
    ## Various combined minor piece features:
    nb_pref = 0
    nb_develop = 0

    pref_turns = 0
    develop_turns = 0
    fully_developed = False

    ## Iterate through board states:
    for i in range(len(game_dict['board_states'])):
        board = game_dict['board_states'][i]
        white_pieces, black_pieces = get_piece_locations(board)
        

        ## Count 'developed' minor pieces
        if (not fully_developed):
            develop_turns += 1
            minor_pieces = []
            for knight in white_pieces['N']:
                minor_pieces.append(knight)
                if knight[1] > 0:
                    nb_develop += 1

            for bishop in white_pieces['B']:
                minor_pieces.append(bishop)
                if bishop[1] > 0:
                    nb_develop -= 1

            developed = [(piece[1] > 0) for piece in minor_pieces]

            fully_developed = all(developed)
    
        ## add +1 for each knight, -1 for each bishop in play for white, subtract those values for black 
        # (if both players have the same number of minor pieces):
        if ((len(white_pieces['N']) + len(white_pieces['B'])) == (len(black_pieces['B']) + len(black_pieces['N']))):
            nb_pref += len(white_pieces['N']) - len(black_pieces['N'])
            nb_pref -= len(white_pieces['B']) - len(black_pieces['B'])
            pref_turns += 1

    ## As always, we normalize by turns we are considering:
    if (pref_turns > 0):
        nb_pref = nb_pref / pref_turns
    if (develop_turns > 0):
        nb_develop = nb_develop / develop_turns 
    return_dict = {'wn_b_trade_pref':nb_pref, 'wn_b_develop_pref' : nb_develop}
    return return_dict

def rook_features(game_dict):
    ## Some helpful variables
    open_files = 0          # Measured in (mid_game_turn, end_game_turn)
    semi_open_files = 0     # Measured in (mid_game_turn, end_game_turn)
    back_rank_rook = 0      # Measured in (0, end_game_turn)
    doubled_rooks = 0       # Measured in (mid_game_turn, end_game_turn)
    doubled_with_queen = 0  # Measured in (mid_game_turn, end_game_turn)
    rook_mobility = 0       # Measured in (mid_game_turn, end_game_turn)

    back_rank = 6

    rook_turns = 0
    
    ## Get middle and end game indices if they exist
    # Set them to the end of the game if they do not
    mid_game_turn = game_dict['middle_game_index']
    if (mid_game_turn == None):
        mid_game_turn = len(game_dict['board_states']) - 1

    end_game_turn = game_dict['end_game_index']
    if (end_game_turn == None):
        end_game_turn = len(game_dict['board_states']) - 1

    ## Iterate through the early game
    # back_rank_rook is the only feature to be detected here 
    for i in range(mid_game_turn):
        board = game_dict['board_states'][i]

        white_pieces, black_pieces = get_piece_locations(board)
        rooks = white_pieces['R']
        ## For each rook, check if its on the opponents back pawn rank
        # (change the back_rank variable to test for black)
        for rook in rooks:
            if (rook[1] == back_rank):
                back_rank_rook += 1

    ## Iterate through the middle game
    # All rook features get tested here
    for i in range(mid_game_turn, end_game_turn):
        board = game_dict['board_states'][i]

        white_pieces, black_pieces = get_piece_locations(board)
        rooks = white_pieces['R']
        queens = white_pieces['Q']
        if (len(rooks) > 0):
            rook_turns += 1
        ## Check individual rook properties
        for rook in rooks:
            if (rook[1] == back_rank):
                back_rank_rook += 1
            ## My favorite line of python to date
            if all([rook[0] != pawn[0] for pawn in white_pieces['P']]):
                if all([rook[0] != pawn[0] for pawn in black_pieces['P']]):
                    open_files += 1
                else:
                    semi_open_files += 1
            for rook2 in rooks:
                ## Check if the rooks are on the same file
                if ((rook[0] == rook2[0]) and (rooks.index(rook) < rooks.index(rook2))):
                    doubled_rooks += 1

            for queen in queens:
                if (rook[0] == queen[0]):
                    doubled_with_queen += 1
        ## We load in the FEN, and make it a pychess Board object to calculate legal moves more quickly
        fen_board = chess.Board(game_dict['board_states_FEN'][i])
        for move in fen_board.legal_moves:
            if (str(fen_board.piece_at(move.from_square)) == 'R'):
                rook_mobility += 1


        ## Normalize all the metrics by game length:
        # But don't want to divide by zero:
    if (end_game_turn - mid_game_turn > 0):
        open_files = open_files/ (end_game_turn - mid_game_turn)
        semi_open_files = semi_open_files / (end_game_turn - mid_game_turn)
        doubled_rooks = doubled_rooks / (end_game_turn - mid_game_turn)
        doubled_with_queen = doubled_with_queen / (end_game_turn - mid_game_turn)
    if rook_turns > 0:
        rook_mobility = rook_mobility / rook_turns
    if (end_game_turn > 0):
        back_rank_rook = back_rank_rook / end_game_turn
    return_dict = {'wopen_files' : open_files, 'wsemi_open_files' : semi_open_files, 'wback_rank_r' : back_rank_rook, 'wdoubled_r' : doubled_rooks, 'wdoubled_with_q' : doubled_with_queen, 'wr_mobility' : rook_mobility}

    return return_dict

def queen_features(game_dict):
    ## Some helpful variables
    queen_aggression = 0     # Measured in (0, mid_game_turn)
    queeinchetto = 0        # Measured in (0, mid_game_turn)
    queenvasion = 0         # Measured in (0, end_game_turn)
    queen_mobility = 0       # Measured in (0, end_game_turn)

    back_rank = 6
    queen_turns = 0

    ## Get middle and end game indices if they exist
    # Set them to the end of the game if they do not
    mid_game_turn = game_dict['middle_game_index']
    if (mid_game_turn == None):
        mid_game_turn = len(game_dict['board_states']) - 1

    end_game_turn = game_dict['end_game_index']
    if (end_game_turn == None):
        end_game_turn = len(game_dict['board_states']) - 1

    for i in range(mid_game_turn):
        board = game_dict['board_states'][i]

        white_pieces, black_pieces = get_piece_locations(board)
        queens = white_pieces['Q']
        if (len(queens) > 0):
            queen_turns += 1
        for queen in queens:
            ## For black, turn this into 7 - queen[1]
            queen_aggression += queen[1]
            
            ## Check for queeinchettos
            if ((queen == (1,1)) or (queen == (6,1))):
                queeinchetto = 1

            if (queen[1] == back_rank):
                queenvasion += 1

        fen_board = chess.Board(game_dict['board_states_FEN'][i])
        ## Sum up all possible queen moves
        for move in fen_board.legal_moves:
            if (str(fen_board.piece_at(move.from_square)) == 'Q'):
                queen_mobility += 1

    for i in range(mid_game_turn, end_game_turn):
        board = game_dict['board_states'][i]

        white_pieces, black_pieces = get_piece_locations(board)
        queens = white_pieces['Q']

        for queen in queens:
            if (queen[1] == back_rank):
                queenvasion += 1

        fen_board = chess.Board(game_dict['board_states_FEN'][i])

        for move in fen_board.legal_moves:
            if (str(fen_board.piece_at(move.from_square)) == 'Q'):
                queen_mobility += 1

    ## As always, the normalization:
    if (mid_game_turn > 0):
        queeinchetto = queeinchetto / mid_game_turn
    if (end_game_turn > 0):
        queenvasion = queenvasion / end_game_turn
        queen_mobility = queen_mobility / end_game_turn
    if (queen_turns > 0):
        queen_aggression = queen_aggression / queen_turns 
    return_dict = {'wq_aggression' : queen_aggression, 'wq_fianchetto' : queeinchetto, 'wq_invasion' : queenvasion, 'wq_mobility' : queen_mobility}

    return return_dict
### White development
### Outputs a list [A,B,C,D,A#,B#,C#,D#,E#,side] where
### A,B,C,D : one-hots for ECO codes (omit E)
### A#,B#,C#,D#,E# : interaction terms, the one-hot times the number of the opening
### side : Float in [-1,1] i.e. Queen to King for white's preferred side to develop onto
###       Measures this by finding the center of mass of certain squares at the mid early game
###       The squares I'll consider are those that don't have the same piece that they started with
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
    
    # Index of halfway through the early game
    index = mid_earlygame(game_dict)
        
    # Find the pieces moved at that index
    pieces = [row[:2] for row in game_dict['board_states'][index]]
    starting_board = [['R', 'P'], ['N', 'P'], ['B', 'P'], ['Q', 'P'], ['K', 'P'], ['B', 'P'], ['N', 'P'], ['R', 'P']]
    pieces_moved = 0
    weight = 0
    for i in range(8):
        for j in range(2):
            if pieces[i][j] != starting_board[i][j]:
                pieces_moved = pieces_moved + 1
                weight = weight + i
    output[-1] = (weight / pieces_moved) / 3.5 - 1
    
    return {'A': output[0],'B': output[1],'C': output[2],'D': output[3],
            'A#': output[4],'B#': output[5],'C#': output[6],'D#': output[7],'E#': output[8],'w_development_side': output[9]}

### White castling
### Outputs a list [earliness, side, side_relative, artificial, development] where
### earliness : float in [0,1], 1/(the turn they castled), 0 if no castle
### side : +1 for king side, -1 for queen side, 0 for no castle
### side_relative : +1 for same side as opponent, -1 for opposite side, 0 if one of them didn't castle
### artificial : 0 if bonafide castle, 1 if artificial
### development : float in [0,1] for how empty the back rank opposite their castling side is
###               calculated as 1 - (# pieces there) / 3, 0 if no castling
### So if white castles and they developed their queen side N and B but the R is still there, then development = 0.66
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
        
    return {'wc_earliness': earliness, 'wc_side': side_white,
            'wc_relative': side_relative, 'wc_artificial': artificial_white, 'wc_development': development}


### White pawns
### Outputs a list
### [king_protection, center_strength, doubled, isolated, backward, tension, color
###    forwardness, guarded_forwardness, en_passant, storming, chain_count, longest_chain, non_queen]
### where
### king_protection : weighted sum of distance of some of my pawns to my king, measured at half midgame
### center_strength : weighted sum of how central guarded pawns are, averaged over midgame
### doubled : average number of doubled pawns throughout midgame. 3 pawns on a file = 2 doubled pawns.
### isolated : similar to previous. 2 pawns on an isolated file = 2 isolated pawns.
### backward : similar to previous. 2 pawns on a file, both behind the neighboring pawns, = 2 backward pawns.
### tension : number of pawn captures available to white's pawns, averaged throughout midgame
### color : float in [-1,1] for average color of my pawn squares at start of endgame (+1 all white, -1 all black)
### forwardness : average rank of my pawns, averaged over the midgame
### guarded_forwardness : sum of ranks of guarded pawns on rank >=4 (index >= 3), -3 for each one, averaged over the midgame
###                       the point of the -3 is so that rank 4 is worth 0 points, rank 5 is worth 1, etc.
### en_passant : float in [0,1], fraction of midgame pawn moves that are en passant
### storming : average of 1 / (distance of my pawns to opponent king), averaged over midgame
###            the rationale for the reciprocal is that if I have no pawns, 0 indicates there are 'infinity far' from the king
###            and also, having pawns that are 6 vs 7 squares from the opponent king is pretty similar
### chain_count : average over midgame of number of len >= 3 pawn chains
### longest_chain : average over midgame of length of longest pawn chain
### non_queen : fraction of promotions that are to a piece other than queen, 0 if no promotions
###
### If the midgame had length 0, pretend it had length 1
def white_pawns(game_dict):
    
    # First get all the relevant indices for board_states
    midgame_index = game_dict['middle_game_index']
    mid_midgame_index = mid_midgame(game_dict)
    endgame_index = game_dict['end_game_index']
    
    # If any of these are None then that could mess with computations
    # So replace None with the maximum index
    midgame_index = cap_index(midgame_index, game_dict)
    mid_midgame_index = cap_index(mid_midgame_index, game_dict)
    endgame_index = cap_index(endgame_index, game_dict)
    
    # In case there was no midgame, pretend there was a midgame of length 1
    if endgame_index == midgame_index:
        endgame_index = midgame_index + 1
    
    ## First calculate the stats that aren't averaged over the midgame
    
    ## King protection
    # Only consider pawns within 2 horizontally and 3 vertically from our king
    # Pawns within 1 horizontally from king get weight 1
    # Pawns 2 horizontally from king get weight 0.5
    # When P is n units from K vertically, I'll assign some float [0,1] of 'protection' it gives to K
    king = game_dict['white_pieces'][mid_midgame_index]['K'][0]
    pawns = game_dict['white_pieces'][mid_midgame_index]['P']
    king_protection = 0
    for pawn in pawns:
        m = abs(pawn[0]-king[0])
        n = abs(pawn[1]-king[1])
        # Check we're not too far from the king
        if (m > 2) | (n > 3): continue
        # Assign weight to the pawn
        protection = 0
        if n == 1:
            protection = 1
        elif n == 2:
            protection = 0.8
        elif n == 3:
            protection = 0.4
        # If it's 2 horitontally from the king,
        if m == 2:
            protection = protection / 2
        king_protection = king_protection + protection
    
    ## Color
    pawns = game_dict['white_pieces'][endgame_index]['P']
    # If the sum of the coords is even it is dark square, if it is odd it is light square
    # So this next array has 1 for light square, 0 for dark square; the mean is the fraction light square
    color = np.mean([(pawn[0] + pawn[1]) % 2 for pawn in pawns])
    
    # Next, scale so that it is in the range [-1,1], 0 if there were no pawns
    if np.isnan(color):
        color = 0
    else:
        color = (color * 2) - 1
        
    ## En passant
    # We have indices for board states, so the indices for white's moves will be (roughly) the same but divided by 2
    # Almost issue: if midgame_index is the last index of board_states and is odd,
    #  taking ceil() will give an index out of range for white_moves
    # But in that case, endgame_index will also be that maximal value (+1)
    # So ceil(midgame_index) > floor(endgame_index), thus there's no indexing issue because we get the empty list
    moves = game_dict['white_moves'][int(np.ceil(midgame_index / 2)) : int(np.floor(endgame_index / 2))]
    pawn_moves = [move for move in moves if move['piece'] == 'P']
    en_passant_moves = [1 for move in pawn_moves if move['special'] == 'p']
    en_passant = len(en_passant_moves) / max(len(pawn_moves),1)
    
    
    ## Non-queen
    moves = game_dict['white_moves']
    promotions = [move for move in moves if ((move['piece'] == 'P') & (move['to'][1] == 7))]
    if len(promotions) == 0:
        non_queen = 0
    else:
        non_queen_promotions = [1 for move in promotions if move['special'] != 'Q']
        non_queen = len(non_queen_promotions) / len(promotions)
    
    ## Now calculate the stats that are averaged over the midgame
    # So have a list of running totals to be averaged at the end
    
    # For each board state, calculate the stats and add to the running totals
    # totals = [center, doubled, isolated, backwards, forward, guarded_forward, storming, chains, long_chains]
    # At the end, take the averages
    totals = np.zeros(10)
    
    for i in range(midgame_index,endgame_index):
        # Things from the dictionary
        FEN = game_dict['board_states_FEN'][i]
        pawns = game_dict['white_pieces'][i]['P']
        
        # If we're out of pawns nothing will be added to the running totals, so we're done
        if len(pawns) == 0: break
        
        ## Center strength
        center_strength = 0
        for pawn in pawns:
            x = pawn[0]
            y = pawn[1]
            # Only look at c,d,e,f file pawns that are guarded
            if (x > 1) & (x < 6) & (len(is_guarded(pawn,FEN)) > 0):
                # The center presence of the pawn is 1 / (its Euclidean distance to the center of the board)
                center_strength = center_strength + 1 / np.sqrt((x-3.5)**2 + (y-3.5)**2)
        
        
        ## Doubled, isolated, backward pawns
        doubled = 0
        isolated = 0
        backward = 0
        
        # Reformat our list of tuples as a list of pawn ranks on each file
        file_rank = [[pawn[1] for pawn in pawns if pawn[0] == file] for file in range(8)]
        # For each file, check
        # 1. How many pawns are on it? If 0, skip the next steps.
        # 2. Are there pawns on adjacent files? If 0, skip the next step.
        # 3. How many of the pawns are behind their neighbor(s)?
        for j in range(8):
            # Get lists for the ranks of pawns on our file and adjacent files
            center = file_rank[j]
            
            if j == 0:
                left = []
            else:
                left = file_rank[j-1]
                
            if j == 7:
                right = []
            else:
                right = file_rank[j+1]
            
            # 1
            count = len(center)
            if count == 0: continue
            if count > 1: doubled = count - 1
                
            # 2
            if (len(left) == 0) & (len(right) == 0):
                isolated = count
                continue
            
            # 3
            # Since the lists of pawns next to us may be empty, have to be careful about using min()
            if len(left) == 0:
                min_left = 8
            else:
                min_left = min(left)
                
            if len(right) == 0:
                min_right = 8
            else:
                min_right = min(right)
                
            min_neighbor_rank = min(min_left,min_right)
            
            for rank in center:
                if rank < min_neighbor_rank:
                    backward = backward + 1
        
        
        ## Pawn tension
        board = chess.Board(FEN)
        
        # Find squares black pawns occupy
        black = set([chess.square(pawn[0],pawn[1]) for pawn in game_dict['black_pieces'][i]['P']])
        
        # Now for each of our pawns, count how many black pawns it is attacking to get the pawn tension
        tension = 0
        for pawn in pawns:
            attacks = set(board.attacks(chess.square(pawn[0],pawn[1])))
            tension = tension + len(attacks & black)
        
        
        ## Forwardness and guarded_forwardness
        forwardness = np.mean([pawn[1] for pawn in pawns])
        # Find the ranks of the guarded forward pawns
        gf_pawns = [pawn[1] for pawn in pawns if ((pawn[1] > 3) & (len(is_guarded(pawn,FEN)) > 0))]
        guarded_forwardness = sum(gf_pawns) - len(gf_pawns) * 3
        
        
        ## Storming
        # Avg of sum of 1 / Euclidean distance of my pawns to their king
        
        # Location of the enemy king
        king = game_dict['black_pieces'][i]['K'][0]
        storming = np.mean([1 / (np.sqrt((pawn[0]-king[0])**2 + (pawn[1]-king[1])**2)) for pawn in pawns])
        
        
        ## Chains
        
        # Average over midgame of the number of length >=3 pawn chains
        # Avg over midgame of length of longest pawn chain
        # (A pawn chain is pawns in a diagonal, including a single pawn diagonal and a 2 pawn diagonal)

        # Make two lists for checking for diagonals up to the right/left separately, by skewing the pawn positions
        down_skew = [[pawn[0],pawn[1]-pawn[0]] for pawn in pawns]
        up_skew = [[pawn[0],pawn[1]+pawn[0]] for pawn in pawns]
        # In the skewed setting, a pawn chain is a list of pawn coords with the same y and no gaps in the x coords
        # I think the easiest way to detect these is:
        # 1. For each j, take the files of all pawns with y = j
        # 2. Iterate through this list of files, keeping track of when we hit a length 3 chain and of what the longest chain is
        # 3. Combine the results from both the up/down skews

        chain_count = 0
        longest_chain = 0
        
        # 1. Loop over all offsets of the diagonals
        for j in range(-7,8):
            # 2. Use the helper function
            d_count, d_longest = chain_helper(down_skew,j)
            u_count, u_longest = chain_helper(up_skew,j)

            # 3.
            chain_count = chain_count + (d_count + u_count)
            longest_chain = max(d_longest,u_longest,longest_chain)
        
        
        ## Add these values to our running totals
        totals = totals + [center_strength, doubled, isolated, backward, tension,
                           forwardness, guarded_forwardness, storming, chain_count, longest_chain]
    
    # Take that average and give things names
    [center_strength, doubled, isolated, backward, tension,
     forwardness, guarded_forwardness, storming, chain_count, longest_chain] = totals / (endgame_index - midgame_index)
    
    # Le return
    return {'wp_king_protection': king_protection, 'wp_center_strength': center_strength,
            'wp_doubled': doubled, 'wp_isolated': isolated, 'wp_backward': backward,
            'wp_tension': tension, 'wp_color': color, 'wp_forwardness': forwardness, 'wp_guarded_forwardness': guarded_forwardness,
            'wp_en_passant': en_passant, 'wp_storming': storming,
            'wp_chain_count': chain_count, 'wp_longest_chain': longest_chain, 'wp_non_queen': non_queen}


### White board
### Outputs a list
### [rank, file, density, attack, pawn_pref, minor_pref, rook_pref, queen_pref]
### where
### rank : average rank of white's pieces, averaged over the midgame
### file : float in [-1,1], (average file) - 3.5 of white's pieces, averaged over the midgame
### density : float in [0,1]. The density of a piece is (# adjacent squares occupied) / (# adjacent squares),
###           so average that over all pieces and the midgame.
### attack : # of squares attacked, averaged over the midgame
### pawn_pref : float in [0,1], fraction of the pawns on the board that are white's, averaged over the midgame
### minor_pref : similar to previous, counting both knights and bishops
### rook_pref : similar to previous
### queen_pref : similar to previous
###
### If the midgame has length 0, just take their value at the index of the midgame
def white_board(game_dict):
    # First get all the relevant indices for board_states
    midgame_index = game_dict['middle_game_index']
    endgame_index = game_dict['end_game_index']
    midgame_index = cap_index(midgame_index, game_dict)
    endgame_index = cap_index(endgame_index, game_dict)
    
    # In case there was no midgame, pretend there was a midgame of length 1
    if endgame_index == midgame_index:
        endgame_index = midgame_index + 1
    
    # For each board state, calculate the stats and add to the running totals
    # At the end, take the averages
    
    output = np.zeros(8)
    
    for i in range(midgame_index,endgame_index):
        # Things from the dictionary
        white_pieces = game_dict['white_pieces'][i]
        black_pieces = game_dict['black_pieces'][i]
        board_object = chess.Board(game_dict['board_states_FEN'][i])

        # Formats the dictionaries as lists of coordinates of spaces occupied
        white_coordinates = [coords for piece in white_pieces.values() for coords in piece]
        black_coordinates = [coords for piece in black_pieces.values() for coords in piece]

        # Formats the coords as sets of numbers, where each number represents a square occupied
        white_locations = set([chess.square(coords[0],coords[1]) for coords in white_coordinates])
        black_locations = set([chess.square(coords[0],coords[1]) for coords in black_coordinates])
        all_locations = set(white_locations | black_locations)
        
        ## Rank
        rank = np.mean([coords[1] for coords in white_coordinates])
        
        ## File
        file = np.mean([coords[0] for coords in white_coordinates]) - 3.5
        
        ## Density
        # This board of all kings makes it easy to determine the adjacent squares, since that would be the squares a king attacks
        K = 'K'*8
        adjacency_object = chess.Board((K+'/')*7+K)
        
        # Divide the number of pieces adjacent to our pieces by the number of squares adjacent to our pieces
        adjacent_squares = white_locations
        for loc in white_locations:
            adjacent_squares = adjacent_squares | set([square for square in adjacency_object.attacks(loc)])
        density = len(adjacent_squares & all_locations) / len(adjacent_squares)
        
        ## Attack
        # Some nice job security code
        num_attacked = len(set([square for loc in white_locations for square in board_object.attacks(loc)]))
        
        ## Pref
        
        # Pawns
        white = len(white_pieces['P'])
        black = len(black_pieces['P'])
        if white + black == 0:
            pawn_pref = 0.5
        else:
            pawn_pref = white / (white+black)
        
        # Minors
        white = len(white_pieces['N']) + len(white_pieces['B'])
        black = len(black_pieces['N']) + len(black_pieces['B'])
        if white + black == 0:
            minor_pref = 0.5
        else:
            pieces = game_dict['black_pieces'][1::2]
            minor_pref = white / (white+black)
        
        # Rooks
        white = len(white_pieces['R'])
        black = len(black_pieces['R'])
        if white + black == 0:
            rook_pref = 0.5
        else:
            rook_pref = white / (white+black)
        
        # Queens
        white = len(white_pieces['Q'])
        black = len(black_pieces['Q'])
        if white + black == 0:
            queen_pref = 0.5
        else:
            queen_pref = white / (white+black)
        
        # Add to our running totals for the output
        output = output + [rank,file,density,num_attacked,pawn_pref,minor_pref,rook_pref,queen_pref]
    
    output = output / (endgame_index - midgame_index)
    
    return {'wb_rank': output[0], 'wb_file': output[1], 'wb_density': output[2], 'wb_attack': output[3],
            'wb_pawn_pref': output[4], 'wb_minor_pref': output[5], 'wb_rook_pref': output[6], 'wb_queen_pref': output[7]}

### White clusters
### Outputs a list
### [MLL, ML, MM, MR, MRR, BL, BM, BR]
### where the abbreviations are for different rectangles of squares on the board, and their values are
### white's fractional presence in the zones, averaged throughout the midgame
### The zones are (given as ranks/files):
### MLL : 45/a
### ML : 45/bc
### MM : 45/de
### MR : 45/fg
### MRR : 45/h
### BL : 3/abc
### BM : 3/de
### BR : 3/fgh
###
### If the midgame had length 0, just calculate this at the turn of the midgame
def white_clusters(game_dict):
    ## Lots of this is similar to white_board
    
    # First get all the relevant indices for board_states
    midgame_index = game_dict['middle_game_index']
    endgame_index = game_dict['end_game_index']
    midgame_index = cap_index(midgame_index, game_dict)
    endgame_index = cap_index(endgame_index, game_dict)
    
    # In case there was no midgame, pretend there was a midgame of length 1
    if endgame_index == midgame_index:
        endgame_index = midgame_index + 1
        
    # Create sets to represent the square clusters
    MLL_mask = set(chess.SquareSet((chess.BB_RANK_4 | chess.BB_RANK_5) & chess.BB_FILE_A))
    ML_mask  = set(chess.SquareSet((chess.BB_RANK_4 | chess.BB_RANK_5) & (chess.BB_FILE_B | chess.BB_FILE_C)))
    MM_mask  = set(chess.SquareSet((chess.BB_RANK_4 | chess.BB_RANK_5) & (chess.BB_FILE_D | chess.BB_FILE_E)))
    MR_mask  = set(chess.SquareSet((chess.BB_RANK_4 | chess.BB_RANK_5) & (chess.BB_FILE_F | chess.BB_FILE_G)))
    MRR_mask = set(chess.SquareSet((chess.BB_RANK_4 | chess.BB_RANK_5) & chess.BB_FILE_H))
    BL_mask  = set(chess.SquareSet(chess.BB_RANK_3 & (chess.BB_FILE_A | chess.BB_FILE_B | chess.BB_FILE_C)))
    BM_mask  = set(chess.SquareSet(chess.BB_RANK_3 & (chess.BB_FILE_D | chess.BB_FILE_E)))
    BR_mask  = set(chess.SquareSet(chess.BB_RANK_3 & (chess.BB_FILE_F | chess.BB_FILE_G | chess.BB_FILE_H)))
    masks = [MLL_mask,ML_mask,MM_mask,MR_mask,MRR_mask,BL_mask,BM_mask,BR_mask]
    
    output = np.zeros(8)
    
    for i in range(midgame_index,endgame_index):
        # Things from the dictionary
        white_pieces = game_dict['white_pieces'][i]

        # Formats the dictionaries as sets of numbers, where each number represents a square occupied
        white_locations = set([chess.square(coords[0],coords[1]) for piece in white_pieces.values() for coords in piece])
        
        # Updates the running total of our fractions
        output = output + [len(mask & white_locations) / len(mask) for mask in masks]
    # Average
    output = output / (endgame_index - midgame_index)
    
    return {'wcl_MLL': output[0], 'wcl_ML': output[1], 'wcl_MM': output[2], 'wcl_MR': output[3], 'wcl_MRR': output[4],
            'wcl_BL': output[5], 'wcl_BM': output[6], 'wcl_BR': output[7]}

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
	dict = {'P_moves':0, 'N_moves':0, 'B_moves':0, 'R_moves':0, 'Q_moves':0, 'K_moves':0}

	for i in range(0, len(gameDict['white_moves'])):
		piece = gameDict['white_moves'][i]['piece']
		if piece == 'O':
			dict['K_moves'] +=1/len(gameDict['white_moves'])
			dict['R_moves'] +=1/len(gameDict['white_moves'])
		else: 
			piece_code = piece + "_moves"
			dict[piece_code] +=1/len(gameDict['white_moves'])
	return dict

### pins function
### input: gameDict
### output: Dictionary with keys "pin_chances", "pins_given", "time_pinned"
### pin_chances : number of opportunites white had to put black in a pin
### pins_given : number of turns white had black pinned
### time_pinned : arrary of turns for continuous pins

def pins(gameDict):
	#creates a list of current pins
	current_pins = {}	

	#creates a list of total pin and length
	total_pins = []

	#counter for number of turns with black pinned
	pins_given = 0

	#counts number of times black is pinned
	for i in range(0, len(gameDict["black_pieces"])):
		if not i%2:
			for pieces in gameDict["black_pieces"][i].values():
				if len(pieces) == 0: break
				for piece in pieces:
					if is_pinned(piece, gameDict["board_states_FEN"][i]):
						pins_given +=1
	
	#counts pins for white
	for i in range(0, len(gameDict["white_pieces"])):
		if i %2:
			#removes any pieces which are not pinned
			for piece_str in current_pins.copy().keys():
				#converts to piece integer tuple
				piece = [int(piece_str[1]), int(piece_str[4])]
				board = chess.Board(gameDict['board_states_FEN'][i])
				if (not board.piece_at(chess.square(piece[0],piece[1]))) or board.piece_at(chess.square(piece[0],piece[1])).color == chess.BLACK or is_pinned(piece, gameDict["board_states_FEN"][i]) == False:
					total_pins.append(current_pins.pop(piece_str))
			for pieces in gameDict["white_pieces"][i].values():
				if len(pieces) == 0:break
				for piece in pieces:	
					if is_pinned(piece, gameDict["board_states_FEN"][i]):
						if str(piece) in current_pins:
							current_pins[str(piece)] +=1
						else: current_pins[str(piece)] =1

	#pops of all elements at the end
	for key in current_pins.copy().keys():
		total_pins.append(current_pins.pop(key))
	return {"pins_given":pins_given, "time_pinned":	total_pins}


### forks
### input: game dictionary
### output: number of forks given

def forks(gameDict):
	fork_counter = 0

	for i in range(len(gameDict['white_pieces'])):
		if i %2:
			for pieces in gameDict["white_pieces"][i].values():
				if len(pieces) == 0: break
				for piece in pieces:
					if gives_fork(piece, gameDict["board_states_FEN"][i]):
						fork_counter += 1
					
	return {'fork_counter' : fork_counter}


### pieces_guarded
### input: game dictionary
### output: average (over the mid-game) of number of pieces guarding attacked pieces divided by the number of attacked pieces times the number of pieces for white

def pieces_guarded(gameDict):
	# counters for number of pieces attacked, number of pieces guarding, and number of pieces for white
	pieces_attacked = []
	pieces_guarding = []
	pieces_white = []

	if gameDict["middle_game_index"] : mid_game = gameDict["middle_game_index"]
	else: mid_game = len(gameDict['board_states']) -1

	if gameDict["end_game_index"] : end_game = gameDict["end_game_index"]
	else: end_game = len(gameDict['board_states']) -1

	# loops through moves in the midgame
	for i in range(mid_game, end_game):
		# counter for number of white pieces
		white_pieces_turn = 0
		# finds all white pieces attacked by black and puts them in a list
		board = chess.Board(gameDict["board_states_FEN"][i])
		piece_attacked_turn = []
		
		for pieces in gameDict["white_pieces"][i].values():
			for piece in pieces:
				white_pieces_turn +=  1 
				if board.is_attacked_by(chess.BLACK, chess.square(piece[0],piece[1])): piece_attacked_turn.append(piece)

		# checks which white pieces are defending them (stored as a chess square)
		piece_defending_turn = set()
		
		for piece in piece_attacked_turn:
			for sq in board.attackers(chess.WHITE, chess.square(piece[0], piece[1])): 
				piece_defending_turn.add(sq)

		pieces_attacked.append(len(piece_attacked_turn))
		pieces_guarding.append(len(piece_defending_turn))
		pieces_white.append(white_pieces_turn)

		p_a = np.array(pieces_attacked)		
		p_g = np.array(pieces_guarding)
		p_w = np.array(pieces_white)

		cum_sum = 0
		for i in range(len(p_a)):
			cum_sum += p_a[i] / max(1, p_g[i] * p_w[i])	

		mean = cum_sum / max(1, len(p_a))
	return {'pieces_guarded' :mean / max(1, (end_game - mid_game))}

### trades
### input: game dictionary
### output: 'num_trades' : number of trades in a game, 'num_direct_trades' : number of direct trades (pieces are traded on the same square), 'num_indirect_trades' : number of indirect trades
### 			(equal material traded on different squares), 'num_direct_trades_white' : number of direct trades initiated by white, 'num_indirect_trades_white' : number of indirect trades initiated by white, 
###			'avg_time_between_direct_trade' :number of white moves between black capturing on a direct trade and white recapturing divided by number of such trades
def trades(gameDict):
	trades_list = []
	trade_moves = []

	if gameDict["middle_game_index"] : mid_game = gameDict["middle_game_index"]
	else: mid_game = len(gameDict['board_states']) -1

	if gameDict["end_game_index"] : end_game = gameDict["end_game_index"]
	else: end_game = len(gameDict['board_states']) -1

	
	#looks first for direct trades
	for i in range(min(len(gameDict['black_moves']), end_game //2 + 1)):

		#checks if there is a white capture and that the move has not already been added to a trade
		if gameDict['white_moves'][i]['capture'] != '' and 2*i not in trade_moves:

			# if piece values are the same, we check first for a direct trade
			if PIECE_VALUES[gameDict['white_moves'][i]['piece']] == PIECE_VALUES[gameDict['white_moves'][i]['capture']]:
				square = gameDict['white_moves'][i]['to']
				for j in range(0,3):
					if i+j >= len(gameDict['black_moves']): break

					#checks that white hasn't moved away and if so changes the square
					if j >0 and gameDict['white_moves'][i+j]['from'] == square: square = gameDict['white_moves'][i+j]['to']
	
					#checks if black takes and creates trade data if it does along with marking the move number
					if gameDict['black_moves'][i+j]['to'] == square:
						trade_temp = {
								'initiated' :'white', 
								'white_traded' : gameDict['white_moves'][i]['piece'], 
								'black_traded' : gameDict['white_moves'][i]['capture'], 
								'move_number' : 2*i, 
								'time_to_trade' : j +1 , 
								'type' : 'direct'
						}
						trades_list.append(trade_temp) 
						trade_moves.append(2*(i+j) +1)
						trade_moves.append(2*i)
						break

		#now goes to black moves and checks if there is a direct trade
		if gameDict['black_moves'][i]['capture'] != '' and 2*i +1 not in trade_moves:

			#check if piece values are the same
			if PIECE_VALUES[gameDict['black_moves'][i]['piece']] == PIECE_VALUES[gameDict['black_moves'][i]['capture']]:
				square = gameDict['black_moves'][i]['to']
				for j in range(1,4): 
					if i+j >=  len(gameDict['white_moves']): break
					#checks that black hasn't moved away and if so changes the square
					if j > 1 and i+j < len(gameDict['black_moves']) and gameDict['black_moves'][i+j]['from'] == square: square = gameDict['black_moves'][i+j]['to']

					#checks if white takes and creates trade data if it does along with marking the move number
					if gameDict['white_moves'][i+j]['to'] == square:
						trade_temp = {'initiated' :'black', 'white_traded' : gameDict['black_moves'][i]['capture'], 'black_traded' :gameDict['white_moves'][i+j]['capture'], 'move_number' : 2*i+1, 'time_to_trade' : j, 'type' : 'direct'}
						trades_list.append(trade_temp) 
						trade_moves.append(2*i +1)
						trade_moves.append(2*(i+j))
						break


	for i in range(min(end_game,len(gameDict['black_moves'])//2 + 1)):
		# checks if there is a white capture that is not yet part of a trade
		if gameDict['white_moves'][i]['capture'] != '' and 2* i not in trade_moves and 2* i + 1 not in trade_moves:
				piece_value = PIECE_VALUES[gameDict['white_moves'][i]['capture']]
		
				#checks next move of black to see if they've taken a piece of the same value
					#checks if black takes and creates trade data if it does
				if gameDict['black_moves'][i]['capture'] in PIECE_VALUES and PIECE_VALUES[gameDict['black_moves'][i]['capture']] == piece_value:
					trade_temp = {'initiated' :'white', 'white_traded' : gameDict['black_moves'][i]['capture'], 'black_traded' :gameDict['white_moves'][i]['capture'], 'move_number' : 2*i, 'time_to_trade' : 1, 'type' : 'indirect'}
					trades_list.append(trade_temp) 
					trade_moves.append(2*(i) + 1)
					trade_moves.append(2*i)
					break 
	
		# checks if there is a black capture that is not yet part of a trade
		if gameDict['black_moves'][i]['capture'] != '' and (2* i +1) not in trade_moves and 2*(i+1) not in trade_moves and 2*(i+1) < len(gameDict['white_moves']):
				piece_value = PIECE_VALUES[gameDict['black_moves'][i]['capture']]
		
				#checks next move of black to see if they've taken a piece of the same value
					#checks if black takes and creates trade data if it does
				if gameDict['white_moves'][i+1]['capture'] in PIECE_VALUES and PIECE_VALUES[gameDict['white_moves'][i+1]['capture']] == piece_value:
					trade_temp = {'initiated' :'black', 'white_traded' : gameDict['black_moves'][i]['capture'], 'black_traded' :gameDict['white_moves'][i+1]['capture'], 'move_number' : 2*i+1, 'time_to_trade' : 1, 'type' : 'indirect'}
					trades_list.append(trade_temp) 
					trade_moves.append(2*(i) + 1)
					trade_moves.append(2*(i+1))
					break 
	
	return {
		'num_trades' : len(trades_list), 
		'num_direct_trades' : sum(1 for trade in trades_list if trade['type'] == 'direct'), 
		'num_indirect_trades' : sum(1 for trade in trades_list if trade['type'] == 'indirect'), 
		'num_direct_trades_white' : sum(1 for trade in trades_list if (trade['type'] == 'direct' and trade['initiated'] == 'white')), 
		'num_indirect_trades_white' : sum(1 for trade in trades_list if (trade['type'] == 'indirect' and trade['initiated'] == 'white')), 
		'avg_time_between_direct_trade' : sum(trade['time_to_trade'] for trade in trades_list if trade['type'] == 'direct' and trade['initiated'] == 'black')/ max(1, sum(1 for trade in trades_list if trade['type'] == 'direct' and trade['initiated'] == 'black'))
		}


### exchanges_possible
### input: game Dict
### output: average number of exchanges for white per move in the middle game

def exchanges_possible(gameDict):
	if gameDict["middle_game_index"] : mid_game = gameDict["middle_game_index"]
	else: mid_game = len(gameDict['board_states']) -1

	if gameDict["end_game_index"] : end_game = gameDict["end_game_index"]
	else: end_game = len(gameDict['board_states']) -1


	exchange_counter = 0
	move_counter = 0
	for i in range(1, end_game, 2):
		board = chess.Board(gameDict['board_states_FEN'][i])
		move_counter += 1
		for pieces in gameDict['white_pieces'][i].values():
			for piece in pieces:
				for attacks in board.attacks(chess.square(piece[0], piece[1])):
					if board.piece_at(attacks) and  board.piece_at(attacks).color == chess.BLACK and PIECE_VALUES[board.piece_at(attacks).symbol().upper()] == PIECE_VALUES[board.piece_at(chess.square(piece[0], piece[1])).symbol().upper()]:
						exchange_counter += 1

	return {'exchanges_possible' :exchange_counter / move_counter}

### king_squares_attacked
### input: gameDict
### output: average number of squares adjacent to king attacked in the midgame

def king_squares_attacked(gameDict):
	if gameDict["middle_game_index"] : mid_game = gameDict["middle_game_index"]
	else: mid_game = len(gameDict['board_states']) -1

	if gameDict["end_game_index"] : end_game = gameDict["end_game_index"]
	else: end_game = len(gameDict['board_states']) -1


	squares_attacked = 0
	
	for i in range(mid_game, end_game):
		board = chess.Board(gameDict['board_states_FEN'][i])
		
		#finds white king
		king = board.king(chess.WHITE)
	
		# iterates through squares adjacent to king and increments counter if attacked
		for square in board.attacks(king):
			if board.is_attacked_by(chess.BLACK, square): squares_attacked +=1

	return {'king_squares_attacked' :squares_attacked / max(1, (end_game - mid_game))}

### king_safety
### input: gameDict
### output: 'king_moves' : counts number of king moves before end game (note: does not count castles) 'king_moves_weighted' : number of king moves times number of black pieces on the board when the move was made, 'distance_from_king' : for a turn calculates the number of king moves away each of black's pieces are from the king divided by the rank of the piece and the sum divided by the number divided by the number of pieces of black's on the board, returns average of this per move before the end game

def king_safety(gameDict):
	if gameDict["middle_game_index"] : mid_game = gameDict["middle_game_index"]
	else: mid_game = len(gameDict['board_states']) -1

	if gameDict["end_game_index"] : end_game = gameDict["end_game_index"]
	else: end_game = len(gameDict['board_states']) -1

	# gets the indexes (in 'white_moves') of the king moves
	move_index = []
	for i in range(min(end_game,len(gameDict['white_moves']))):
		if gameDict['white_moves'][i]['piece'] == 'K': move_index.append(2*i-1)

	# iterates through the board states and calculates distance_from_king metric when reaches a move that is a white king move, also calculates king_moves and kings_moves_weighted
	king_moves = 0
	king_moves_weighted = 0
	distance_from_king_sum = 0
	for i in range(end_game):

		# checks if a king moves and increments the counters
		if i in move_index:
			king_moves +=1
			#calculates material of black			
			king_moves_weighted += material(gameDict, i, chess.BLACK)

		# calculates king square
		king = gameDict['white_pieces'][i]['K'][0]
		distance_from_king_sum_move = 0 
		black_pieces = 1

		for piece in ['P', 'N', 'B', 'R', 'Q']:
			for piece_instance in gameDict['black_pieces'][i][piece]:
				distance_from_king_sum_move += max(abs(king[0] - piece_instance[0]), abs( king[1] - piece_instance[1])) / PIECE_VALUES[piece]
				black_pieces += 1
		
		distance_from_king_sum += distance_from_king_sum_move / black_pieces

	return {'king_moves': king_moves, 'king_moves_weighted' : king_moves_weighted, 'distance_from_king' : distance_from_king_sum / max(1, end_game)}
				
		
### get_url
### input: gameDict
### output: game_id

def get_game_id(gameDict):
	return {'game_id' : gameDict['game_id']}	

### get_white
### input: gameDict
### output: white_player

def get_white(gameDict):
	return {'white_player': gameDict['white_player']}


#######################################################################################
##### Processing Game Features
######################################################################################

### get_features
### input: gameDict
### output: dictionary of all feature dictionaries

def get_features(game):
	return {**get_game_id(game), **get_white(game), **knight_features(game), **bishop_features(game), **minor_features(game), **rook_features(game), **queen_features(game), **white_development(game), **white_castling(game), **white_pawns(game), **white_board(game), **white_clusters(game), **discovered_checks(game), **distribution_piece_moves(game), **pins(game), **forks(game), **pieces_guarded(game), **trades(game), **exchanges_possible(game), **king_squares_attacked(game), **king_safety(game)}
