import chess

import table


def evaluateBoard(board):
    return sum(
        pieceValue(board.piece_at(square), square)
        if board.piece_at(square) is not None else 0
        for square in chess.SQUARES)


def pieceValue(piece, square):
    symbol = piece.symbol()
    is_white = not symbol.islower()

    row = convertSquare(square, is_white)[0]
    column = convertSquare(square, is_white)[1]

    score = 1 if is_white else -1
    if symbol.lower() == 'p':
        score *= (1000 + table.PAWN[row][column])
    elif symbol.lower() == 'n':
        score *= (3000 + table.KNIGHT[row][column])
    elif symbol.lower() == 'b':
        score *= (3000 + table.BISHOP[row][column])
    elif symbol.lower() == 'r':
        score *= (5000 + table.ROOK[row][column])
    elif symbol.lower() == 'q':
        score *= (9000 + table.QUEEN[row][column])
    elif symbol.lower() == 'k':
        score *= (1000000 + table.KING[row][column])
    return score


def convertSquare(square, is_white):
    row = 7 - (square // 8) if is_white else square // 8
    column = square % 8
    return (row, column)

def pieceValues(piece_type):
        #Returns the value for a chess piece. 
        #This heuristic is a common way of ranking the importance of each piece. 
        #This is used as a helper to calculate the entire utility of a board state.  
        #piece_type: a chess.piece.piece_type. Encodes which chess piece we are looking at. 
        #Returns: A number representing the value of the given piece_type. 
        
        if piece_type == chess.PAWN:
            return 1
        
        elif piece_type == chess.KNIGHT or piece_type == chess.BISHOP:
            return 3 
        
        elif piece_type == chess.ROOK:
            return 5
        
        elif piece_type == chess.QUEEN:
            return 9
        
        else:
            #In Chess, the King has no inherent point value attached to it.
            #Since the King cannot be captured, for our purposes it will hold a value of 10.
            return 10 

def calculateBoardValue(board):
    #Returns the board utility value for the provided board. 
    #board: Represents the game board 
    #Returns:
        #> 0    if WHITE is winning. 
        #0      if both WHITE and BLACK have the same utility. 
        #< 0    if BLACK is winning. 
        
    #Getting a dict of pieces from the board 
    piece_map = board.piece_map()
    board_sum = 0
        
    #Iterating over the map of pieces 
    for piece in piece_map.values():
        
        #Increment value if WHITE
        if piece.color == chess.WHITE:
            board_sum += pieceValues(piece.piece_type)
    
        #Decrement value if BLACK
        elif piece.color == chess.BLACK:
            board_sum -= pieceValues(piece.piece_type)
        
    return board_sum
