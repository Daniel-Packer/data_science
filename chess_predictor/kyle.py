import chess

pgn_test = '''forest_clf = RandomForestClassifier(max_depth = 5)[Event "Rated Blitz game"]
[Site "https://lichess.org/5WDTKQIn"]
[Date "2020.05.07"]
[Round "-"]
[White "amacalo"]
[Black "bindercommakyle"]
[Result "1-0"]
[UTCDate "2020.05.07"]
[UTCTime "18:13:20"]
[WhiteElo "1535"]
[BlackElo "1587"]
[WhiteRatingDiff "+7"]
[BlackRatingDiff "-7"]
[Variant "Standard"]
[TimeControl "180+2"]
[ECO "D20"]
[Termination "Normal"]

1. d4 d5 2. c4 dxc4 3. e4 b5 4. a4 Qd7 5. axb5 Qxb5 6. Nc3 Qb3 7. Qf3 Nf6 8. e5 Bg4 9. Qxa8 Ne4 10. Qxe4 1-0'''

### The get_gameDict function reads in a lichess pgn string and returns a game dictionary

### The game dictionary is a dictionary formatted with the following keys:
### 'white_moves' : [list of move dictionaries for white moves (documentation below)]
### 'black_moves' : [list of move dictionaries for black moves]
### 'white_player' : string of the lichess username of the white player
### 'black_player' : string of the lichess username of the black player
### 'opening' : string of the ECO code of the opening
### 'time_control' : string of the time control "starting time (in seconds)+increment time
###									(in seconds)
### 'board_state' : list of board states 2d array of strings (documentation below)
### 'board_state_FEN' : list of FEN strings for the game states

### move dictionary
### the move dictionary has the following keys
### 'piece' : string of the piece moved (ex. 'P', 'R', 'N', 'B', 'K', 'Q')
### 'from' : tuple of integers of the starting square of the piece moved (1,8) corresponds to a8
### 'to' : tuple of integers of the ending square of the piece move
### 'capture' : string of the piece captured (returns empty string if no capture, strings are same as piece)
### 'move_number' : integer of the half move number (ex white's first move is 1, black's is 2)
### 'special' : returns a string giving the following game conditions: en passant = 'p', promotion = piece 
###			character, castle = "O-O" or "O-O-O"
### 'check' : returns a string corresponding to whether or not there is a check or checkmate check = "+",
###				checkmate  = '#', neither is given by empty string

def get_gameDict(gamepgn):
	#creates the game dictionary
	gameDict = {'white_moves' : [], 'black_moves' :[], 'board_states' :[], 'board_states_FEN' :[] }
	
	#reads in white_player
	name_start = gamepgn.find('White "') +7
	name_end = gamepgn.find('"', name_start)
	gameDict["white_player"] = gamepgn[name_start :name_end]
	
	#reads in black_player
	name_start = gamepgn.find('Black "') +7
	name_end = gamepgn.find('"', name_start)
	gameDict["black"] = gamepgn[name_start :name_end]

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
	move_counter = 1

	# creates the FEN for the opening board and creates a chess board object for that
	# state
	current_board = chess.Board(chess.STARTING_FEN)
	
	#writes the first FEN
	gameDict["board_states_FEN"].append(current_board.fen())

	for move in move_list:
		move_dict = {"move_number": move_counter, "capture" : None, "check" : None, "special": None}
		#checks what piece was moved
		if move[0].isupper():
			move_dict["piece"] = move[0]
		else:
			move_dict["piece"] = "P"

		#parses the next move
		current_move = current_board.parse_san(move)
		

		####MUST MVE DOWN
		#writes the new FEN
		#gameDict["board_states_FEN"].append(current_board.fen())

		#writes the to and from squares
		move_dict["to"] = chess.SQUARE_NAMES[current_move.to_square]
		move_dict["from"] = chess.SQUARE_NAMES[current_move.from_square]		
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
			gameDict["white_moves"].append(move_dict)
		else: 
			gameDict["black_moves"].append(move_dict) 

		#pushes the move and writes the new FEN
		current_board.push(current_move)
		gameDict["board_states_FEN"].append(current_board.fen())

		#writes the array state
		board_copy = current_board.copy()
		board_state =  [[None for i in range(0,8)] for j in range(0,8)]
		for rank in range(0,8):
			for column in range(0,8):
				piece = board_copy.remove_piece_at(chess.SQUARES[8*rank + column ])
				if piece: board_state[rank][column] = piece.symbol().upper()
	
		#check is mate or checkmate
		if current_board.is_check(): move_dict["check"] = "+"
		elif current_board.is_checkmate(): move_dict["check"] = "#"
				
		move_counter += 1


	return gameDict

