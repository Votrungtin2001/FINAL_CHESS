from numpy import True_
import configs 
import tkinter
from PIL import Image, ImageTk

import chess

ROW_NUMBER = configs.ROW_NUMBER
COLUMN_NUMBER = configs.COLUMN_NUMBER
ROW_CHARS = configs.ROW_CHARS
WHITE = configs.WHITE
BLACK = configs.BLACK
YELLOW = configs.YELLOW
GREEN = configs.GREEN

class GUI(tkinter.Frame):

    def __init__(self, root, parent, board, playerTurns, mode):
        #Construction
        self.SQUARE_SIZE = configs.SQUARE_SIZE
        self.pieces = {}
        self.icons = {}
        self.selectedPiece = None
        self.startSquare = None
        self.highlightedPieces = []

        self.root = root
        self.parent = parent
        self.board = board
        self.playerTurns = playerTurns #True means white, False means black
        self.mode = mode

        #Frame
        tkinter.Frame.__init__(self, root)

        #Set up canvas
        CANVAS_WIDTH = COLUMN_NUMBER * self.SQUARE_SIZE
        CANVAS_HEIGHT = ROW_NUMBER * self.SQUARE_SIZE

        self.canvas = tkinter.Canvas(
            self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background='grey')
        self.canvas.pack(side='top', fill='both', anchor='c', expand=True)
        self.canvas.bind('<Button-1>', self.click)

        #Drawing
        self.refresh()
        self.drawPieces()

        #Status bar
        self.statusbar = tkinter.Frame(self, height=32)
        self.label_status = tkinter.Label(self.statusbar, text='', fg='black')
        self.label_status.pack(side=tkinter.LEFT, expand=0, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill='x', side='bottom')

    def click(self, event):
        #Unenable clicks if not in player's turn
        playerTurn = self.playerTurns[-1]
        if(playerTurn == False and self.mode != "humanHuman") or (self.mode == "minimaxMCTS"):
            return None

        COLUMN_SIZE = ROW_SIZE = event.widget.master.SQUARE_SIZE
        row = int(8 - (event.y / ROW_SIZE))
        column = int(event.x / COLUMN_SIZE)
        position = (row, column)

        #Check if player is selecting their other piece
        piece = self.board.piece_at(row * 8 + column)
        isOwn = False
        if piece is not None and self.selectedPiece is not None:
            isPieceLower = piece.symbol().islower()
            isSelectedPieceLower = self.selectedPiece.symbol().islower()

            isOwn = not isPieceLower  ^ isSelectedPieceLower

        #Move it or replace it
        if self.selectedPiece is None or isOwn:
            self.selectedPiece = piece
            self.startSquare = (row, column)

            self.highlight() #Highlight the square

        else:
            self.move(destSquare=position)

            self.selectedPiece = None
            self.startSquare = None

            self.pieces = {}
            self.highlightedPieces = []

        self.refresh()
        self.drawPieces()

    def move(self, destSquare):
        #Making move notation, such as e2e4
        move = ROW_CHARS[self.startSquare[1]] + str(self.startSquare[0] + 1)
        move += ROW_CHARS[destSquare[1]] + str(destSquare[0] + 1)

        legalMoves = [str(legal_move) for legal_move in self.board.legal_moves]

        #Handle pawn promotion
        if move + 'q' in legalMoves:
            move += 'q'

        if move in legalMoves:
            self.board.push(chess.Move.from_uci(move))
            
            if(self.playerTurns[-1] == True): self.playerTurns.append(False)
            else: self.playerTurns.append(True)

            if self.board.is_checkmate():
                if(self.isWhiteTurn == True): text = "Checkmate. Black won"
                else: text = "Checkmate. White won"
                self.label_status['text'] = text

            elif self.board.is_stalemate():
                self.label_status['text'] = "It was a draw match."

            else:
                playerTurn = self.playerTurns[-1]
                if(playerTurn == True and self.mode != "mctsMinimax"):
                    self.root.after(100, self.parent.playerPlay)
                elif(playerTurn == False and self.mode == "humanHuman"):
                    self.root.after(100, self.parent.playerPlay)
                else:
                    if(playerTurn == True and self.mode == "mctsMinimax"):
                        self.label_status['text'] = "CPU(Minimax)'s turn - White. The computer is thinking..."
                    elif(playerTurn == False and self.mode == "mctsMinimax"):
                        self.label_status['text'] = "CPU(MCTS)'s turn - Black. The computer is thinking..."
                    elif(playerTurn == False and self.mode != "mctsMinimax" and self.mode != "humanHuman"):
                        self.label_status['text'] = "Computer's turn - Black. The computer is thinking..."
                    self.root.after(100, self.parent.computerPlay)
                
        else:
            self.label_status['text'] = "Wrong move, please try again."

    def highlight(self):
        self.highlightedPieces = []

        legalMoves = [str(legal_move) for legal_move in self.board.legal_moves]

        selectedSquare = ROW_CHARS[self.startSquare[1]] + str(
            self.startSquare[0] + 1)

        self.highlightedPieces = [(int(legal_move[-1]) - 1,
                                    ROW_CHARS.index(legal_move[2])) if
                                   selectedSquare == legal_move[:2] else None
                                   for legal_move in legalMoves]

    def refresh(self, event={}):
        if event:
            X_SIZE = int((event.width - 1) / COLUMN_NUMBER)
            Y_SIZE = int((event.height - 1) / ROW_NUMBER)
            self.SQUARE_SIZE = min(X_SIZE, Y_SIZE)

        self.canvas.delete('square')
        color = BLACK

        for row in range(ROW_NUMBER):
            color = WHITE if color == BLACK else BLACK

            for col in range(COLUMN_NUMBER):
                startColumn = (col * self.SQUARE_SIZE)
                startRow = ((7 - row) * self.SQUARE_SIZE)
                endColumn = startColumn + self.SQUARE_SIZE
                endRow = startRow + self.SQUARE_SIZE

                if (row, col) in self.highlightedPieces:
                    self.canvas.create_rectangle(
                        startColumn,
                        startRow,
                        endColumn,
                        endRow,
                        outline='',
                        fill=YELLOW,
                        tags='square')
                elif ((row, col) == self.SQUARE_SIZE) and (self.selectedPiece is not None):
                    self.canvas.create_rectangle(
                        startColumn,
                        startRow,
                        endColumn,
                        endRow,
                        outline='',
                        fill=GREEN,
                        tags='square')
                else:
                    self.canvas.create_rectangle(
                        startColumn,
                        startRow,
                        endColumn,
                        endRow,
                        outline='',
                        fill=color,
                        tags='square')

                color = WHITE if color == BLACK else BLACK

        for name in self.pieces:
            self.placePiece(name, self.pieces[name][0], self.pieces[name][1])

        self.canvas.tag_raise('piece')
        self.canvas.tag_lower('square')

    def drawPieces(self):
        self.canvas.delete('piece')

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            PIECE_NAME = ""

            if piece is not None:
                if(str(piece) == "b"): PIECE_NAME = "black_bishop"
                if(str(piece) == "k"): PIECE_NAME = "black_king"
                if(str(piece) == "n"): PIECE_NAME = "black_knight"
                if(str(piece) == "p"): PIECE_NAME = "black_pawn"
                if(str(piece) == "q"): PIECE_NAME = "black_queen"
                if(str(piece) == "r"): PIECE_NAME = "black_rook"
                if(str(piece) == "B"): PIECE_NAME = "white_bishop"
                if(str(piece) == "K"): PIECE_NAME = "white_king"
                if(str(piece) == "N"): PIECE_NAME = "white_knight"
                if(str(piece) == "P"): PIECE_NAME = "white_pawn"
                if(str(piece) == "Q"): PIECE_NAME = "white_queen"
                if(str(piece) == "R"): PIECE_NAME = "white_rook"

                IMAGE_NAME = 'src/images/' + PIECE_NAME + '.png'
                piece_name = '%s%s' % (piece.symbol(), square)

                if IMAGE_NAME not in self.icons:
                    image = Image.open(IMAGE_NAME).resize((64, 64))
                    self.icons[IMAGE_NAME] = ImageTk.PhotoImage(image)

                row = square // 8
                column = square % 8

                self.addPiece(piece_name, self.icons[IMAGE_NAME], row, column)
                self.placePiece(piece_name, row, column)

    def addPiece(self, name, image, row=0, column=0):
        self.canvas.create_image(
            0, 0, image=image, tags=(name, 'piece'), anchor='c')
        self.placePiece(name, row, column)

    def placePiece(self, name, row, column):
        self.pieces[name] = (row, column)

        ROW_SIZE = (column * self.SQUARE_SIZE) + (self.SQUARE_SIZE // 2)
        COLUMN_SIZE = ((7 - row) * self.SQUARE_SIZE) + (self.SQUARE_SIZE // 2)

        self.canvas.coords(name, ROW_SIZE, COLUMN_SIZE)
