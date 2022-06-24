import pickle
from chess.polyglot import open_reader
import chess
from random import randint
from board import evaluateBoard
import time


class MinimaxAlgorithm:
    #For minimax algorithm
    depth = 3
    boardCaches = {}
    cacheHit = 0
    cacheMiss = 0

    #Set up cache 
    try:
        cache = open('data/cache.p', 'rb')
    except IOError:
        #Create new file cache.p when it is not existed
        cache = open('data/cache.p', 'wb')
        pickle.dump(boardCaches, cache)
    else:
        #Load cache when it existed
        boardCaches = pickle.load(cache)

    def __init__(self, board, isWhitePlayer):
        self.board = board

        #Not color of player (human)
        self.isWhitePlayer = isWhitePlayer

        with open_reader('data/opening.bin') as reader:
            self.openingMoves = [
                str(entry.move) for entry in reader.find_all(board)
            ]
    
    def minimaxMove(self):
        globalScore = -1e8 if self.isWhitePlayer else 1e8
        selectedMove = None

        #Can move from opening book
        if self.openingMoves:
            selectedMove = chess.Move.from_uci(
                self.openingMoves[randint(0, len(self.openingMoves) // 2)])
        
        else:
            for move in self.board.legal_moves:
                self.board.push(move)

                localScore = self.minimaxAlgorithm(self.depth - 1, not self.isWhitePlayer,
                                           -1e8, 1e8)

                self.boardCaches[self.hashBoard(
                    self.depth - 1, not self.isWhitePlayer)] = localScore

                if self.isWhitePlayer and localScore > globalScore:
                    globalScore = localScore
                    selectedMove = move
                elif not self.isWhitePlayer and localScore < globalScore:
                    globalScore = localScore
                    selectedMove = move

                self.board.pop()
                print(localScore, move)

            print('\ncacheHit: ' + str(self.cacheHit))
            print('cacheMiss: ' + str(self.cacheMiss) + '\n')

        print("The selected move after running minimax algorithm:")
        print(str(globalScore) + ' ' + str(selectedMove) + '\n')

        self.board.push(selectedMove)

        with open('data/cache.p', 'wb') as cache:
            pickle.dump(self.boardCaches, cache)


    #The max node has an alpha value (greater than or equal to alpha – always increasing).
    #The min node has a beta value (less than or equal to beta – always decreasing). 
    #When the alpha and beta are not determined, perform a depth-first search to determine the alpha, beta, 
    #and propagate back to the parent nodes.
    def minimaxAlgorithm(self, depth, isMaxingWhite, alpha, beta):
        #If board in cache
        if self.hashBoard(depth, isMaxingWhite) in self.boardCaches:
            self.cacheHit += 1

            return self.boardCaches[self.hashBoard(depth, isMaxingWhite)]

        self.cacheMiss += 1

        #If depth is 0 or game is over
        if depth == 0 or not self.board.legal_moves:
            self.boardCaches[self.hashBoard(
                depth, isMaxingWhite)] = evaluateBoard(self.board)
            return self.boardCaches[self.hashBoard(depth, isMaxingWhite)]

        #Else
        best_score = -1e8 if isMaxingWhite else 1e8
        for move in self.board.legal_moves:
            self.board.push(move)

            local_score = self.minimaxAlgorithm(depth - 1, not isMaxingWhite, alpha,
                                       beta)
            self.boardCaches[self.hashBoard(
                depth - 1, not isMaxingWhite)] = local_score

            if isMaxingWhite:
                best_score = max(best_score, local_score)
                alpha = max(alpha, best_score)
            else:
                best_score = min(best_score, local_score)
                beta = min(beta, best_score)

            self.board.pop()

            if beta <= alpha:
                break

        self.boardCaches[self.hashBoard(depth, isMaxingWhite)] = best_score
        return self.boardCaches[self.hashBoard(depth, isMaxingWhite)]

    #Create string to print in terminal
    def hashBoard(self, depth, isMaxingWhite):
        return str(self.board) + ' ' + str(depth) + ' ' + str(isMaxingWhite)

    def minimaxMove(self, repeatedMinimaxMove, countRepeatedMinimaxMove, turnMinimax, allMinimaxMoves):
        globalScore = -1e8 if self.isWhitePlayer else 1e8
        selectedMove = None

        #Can move from opening book
        if self.openingMoves:
            selectedMove = chess.Move.from_uci(
                self.openingMoves[randint(0, len(self.openingMoves) // 2)])

            #Handle when repeating move
            if(len(repeatedMinimaxMove) > 0):
                if(len(allMinimaxMoves) >= 3):
                    repeatedMove = allMinimaxMoves[-2]
                    if(str(selectedMove) == str(repeatedMove)):
                        countRepeatedMinimaxMove.append(1)
                        repeatedMinimaxMove.append(selectedMove)
        
        else:
            for move in self.board.legal_moves:
                self.board.push(move)

                localScore = self.minimaxAlgorithm(self.depth - 1, not self.isWhitePlayer,
                                           -1e8, 1e8)

                self.boardCaches[self.hashBoard(
                    self.depth - 1, not self.isWhitePlayer)] = localScore

                if self.isWhitePlayer and localScore > globalScore:
                    globalScore = localScore
                    selectedMove = move

                    #Handle when repeating move
                    if(len(repeatedMinimaxMove) > 0):
                        if(len(allMinimaxMoves) >= 3):
                            repeatedMove = allMinimaxMoves[-2]
                            if(str(selectedMove) == str(repeatedMove)):
                                countRepeatedMinimaxMove.append(1)
                                repeatedMinimaxMove.append(selectedMove)

                elif not self.isWhitePlayer and localScore < globalScore:
                    globalScore = localScore
                    selectedMove = move

                    #Handle when repeating move
                    if(len(repeatedMinimaxMove) > 0):
                        if(len(allMinimaxMoves) >= 3):
                            repeatedMove = allMinimaxMoves[-2]
                            if(str(selectedMove) == str(repeatedMove)):
                                countRepeatedMinimaxMove.append(1)
                                repeatedMinimaxMove.append(selectedMove)

                self.board.pop()
                print(localScore, move)

        #Handle when repeating the move
        if(len(repeatedMinimaxMove) > 0):
            if(len(countRepeatedMinimaxMove) >= 2):
                print("repeatedMinimax")
                self.cacheHit = 0
                self.cacheMiss = 0

                repeatedMove = repeatedMinimaxMove[-1]

                count = 0

                for move in self.board.legal_moves:
                    count+=1

                    self.board.push(move)

                    localScore = self.minimaxAlgorithm(self.depth - 1, not self.isWhitePlayer,
                                           -1e8, 1e8)

                    self.boardCaches[self.hashBoard(
                        self.depth - 1, not self.isWhitePlayer)] = localScore

                    if self.isWhitePlayer and localScore > globalScore:
                        if(str(move) != str(repeatedMove)):
                            globalScore = localScore
                            selectedMove = move
                    elif not self.isWhitePlayer and localScore < globalScore:
                        if(str(move) != str(repeatedMove)):
                            globalScore = localScore
                            selectedMove = move

                    self.board.pop()
                    print(localScore, move)

                randomIndex = randint(0, count - 1)
                count = 0
                for move in self.board.legal_moves:
                    count+=1
                    if(randomIndex == count - 1):
                        selectedMove = move


        print('\ncacheHit: ' + str(self.cacheHit))
        print('cacheMiss: ' + str(self.cacheMiss) + '\n')

        print("The selected move after running minimax algorithm:")
        print(str(globalScore) + ' ' + str(selectedMove) + '\n')

        if(turnMinimax == 1): repeatedMinimaxMove.append(selectedMove)

        allMinimaxMoves.append(selectedMove)

        self.board.push(selectedMove)

        with open('data/cache.p', 'wb') as cache:
            pickle.dump(self.boardCaches, cache)
