import minimax_algorithm as Minimax
import monte_carlo_tree_search_algorithm as MCTS

class Computer:

    def __init__(self, board, isWhitePlayer, mode, isMCTS):
        self.board = board
        self.mode = mode
        if(self.mode == "mctsMinimax"):
            if(isWhitePlayer == True):
                self.colorMCTS = True
            else: 
                self.colorMCTS = False
        else: 
            self.colorMCTS = False

        #Not color of player (human)
        self.isWhitePlayer = not isWhitePlayer
        self.isMCTS = isMCTS

    def aiMove(self, turn, repeatedMCTSMove, repeatedMinimaxMove, countRepeatedMCTSMove, countRepeatedMinimaxMove, turnMCTS, turnMinimax, allMCTSMoves, allMinimaxMoves):
        if(self.mode == "humanMinimax"):
            if(self.isWhitePlayer == False):
                print('minimax')
                Minimax.MinimaxAlgorithm(self.board, self.isWhitePlayer).minimaxMove(repeatedMinimaxMove, countRepeatedMinimaxMove, turnMinimax, allMinimaxMoves)

        elif(self.mode == "mctsMinimax"):
            if(self.isMCTS == False):
                print('minimax')
                Minimax.MinimaxAlgorithm(self.board, not self.colorMCTS).minimaxMove(repeatedMinimaxMove, countRepeatedMinimaxMove, turnMinimax, allMinimaxMoves)
            else:
                print('mcts')
                MCTS.MCTSAlgorithm(self.board, self.colorMCTS).MCTSMove(repeatedMCTSMove, countRepeatedMCTSMove, turnMCTS, allMCTSMoves)
               
        elif(self.mode == "humanMCTS"):
            if(self.isWhitePlayer == False):
                print('mcts')
                MCTS.MCTSAlgorithm(self.board, self.colorMCTS).MCTSMove(repeatedMCTSMove, countRepeatedMCTSMove, turnMCTS, allMCTSMoves)



    
