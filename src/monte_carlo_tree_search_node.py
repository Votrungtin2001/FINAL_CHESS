import random
from math import sqrt, log
import copy
from board import calculateBoardValue

class MonteCarloTreeSearchNode:

    def __init__(self, state, parent, parentAction, rolloutStrategy, color):
        #Represents a node for usage in MCTS algorithm.

        #state: The board object representing the state of the game. 
        #parent: The Node object this node was derived from. None for root node. 
        #parentAction: The action taken by parent Node to get to this state. None for root node. 
        #rolloutStrategy (String): Represents which strategy to use for rollouts to end of game.  
   
        #State is a chess.Board: The board to play the player's move on.
        self.state = state 
        #Reference to the parent Node. 
        self.parent = parent 
        #The move taken to arrive at this state from the parent Node. 
        self.parentAction = parentAction
        #Defining an empty list of children Nodes. 
        self.children = []
        #Number of simulations won/lost/tied from this Node. 
        self.wins, self.losses, self.ties = 0, 0, 0 
        #Setting the rollout strategy for this MCTS algorithm
        self.rolloutStrategy = rolloutStrategy
        #Sets which color this AI is playing as
        self.color = color

    def pickMove(self, legalMoves):
        #Picks a random, untaken move from this Node.  
        #legal_moves: list of Move objects. 
        #Returns: A single Move object that does not have a Node built for it yet.  

        #List of all actions taken by the current children of this Node. 
        childActionsTaken = []

        for child in self.children:
            #Looking at children's parentAction field. 
            childActionsTaken.append(child.parentAction)

        #Moves that have not been taken yet 
        untakenMoves = []
    
        for move in legalMoves:
            #Making sure the move has not been taken by a child of this Node.
            if move not in childActionsTaken:
                untakenMoves.append(move)
    
        randIndex = random.randrange(len(untakenMoves))
        randMove = untakenMoves[randIndex]
        return  randMove

    def selection(self):
        #Select a child node in the tree. If all children have been explored, 
        #use the UCB1 formula. Otherwise, expand a random child node. 
        
        if self.state.legal_moves.count() == 0:
            return 

        #Do the selection
        if self.state.legal_moves.count() == len(self.children):        
            #We chose to set c as sqrt(2). Does a good job of balancing exploration and exploitation.
            c = sqrt(2)

            #Get the total number of times we've explored any children.
            totalTimesExplored = self.wins + self.ties + self.losses

            #Calculate all of the ucb1 scores for each node.
            scores = []
            for node in self.children:
                timesExplored = node.wins + node.ties + node.losses
                successRate = (node.wins + (node.ties / 2)) / timesExplored
                ucb1 = self.ucb1(successRate, c, totalTimesExplored, timesExplored)
                scores.append(ucb1)
      
            #Get the node which has the highest ucb1 score.
            selectionIndex = scores.index(max(scores))
            selectionNode = self.children[selectionIndex]

            #Recursively perform selection on the child node we select.
            selectionNode.selection()

        else:
            #Do the expansion 
            self.expansion()

    def expansion(self):
        #Take a random unexplored move, and create a Node for that next state.
        
        #Pick a random move.
        newMove = self.pickMove(self.state.legal_moves)
        
        #Copying the board
        boardCopy = copy.deepcopy(self.state)
        boardCopy.push(newMove)
        newBoard = boardCopy
    
        #Pick a legal move that doesn't have a Node yet.
        #Creating a new node with self as the parent. 
        newNode = MonteCarloTreeSearchNode(newBoard, self, newMove, self.rolloutStrategy, self.color)
        
        #Do simulation on the new node.
        newNode.simulation()

        #Adding the new node to the children of the parent node.
        self.children.append(newNode)

    def randomRollout(self, board):
        #Responsible for picking an available move and doing board.push(move). 
        #In this case, the move is completely random for the random rollout strategy. 
        #board: The representation of the current game board. 

        #Getting a random move from all valid moves.
        legalMoves = board.legal_moves
        randomMove = random.randrange(legalMoves.count())

        i = 0
        for move in legalMoves:
            if i == randomMove:
                #Updating the board.
                board.push(move)
                break

            i += 1

    def attackingRollout(self, board):
        #Out of all the current legal moves, filter for moves that take enemy pieces. 
        #Then find the move with the max value, defined by the piece_values function above. 
        #This is a fairly common heuristic in chess. Where taking more important pieces result in higher rewards. 
        #If there are no attacking moves to play, use random rollout. 
        #board: The representation of the current game board.
         
        legalMoves = board.legal_moves
        maxVal = 0
        maxMovesArray = []

        for move in legalMoves:
            #Checking where the move lands the piece in question.
            landingSquare = move.to_square

            #Checking if the position already has an enemy piece, this represents taking a piece.  
            #piece_val is a number
            pieceVal = board.piece_type_at(landingSquare)
            
            #If move is attacking an opponent piece:
            if pieceVal is not None:
                #If this is the new max move, update.
                if pieceVal > maxVal:
                    #This is a new high score, need a new moves array.
                    maxMovesArray = []
                    maxVal = pieceVal
                    maxMovesArray.append(move)

                elif pieceVal == maxVal:
                    #This is tie for high score, add to the existing array.
                    maxMovesArray.append(move)
    
        #If there is no max move, use random rollout.
        if len(maxMovesArray) == 0:
            self.randomRollout(board)

        elif len(maxMovesArray) == 1:
            #If there is 1 clear best move, commit to it. 
            board.push(maxMovesArray[0])
        
        else:
            #Pick a random move out of the best possible.
            randomIndex = random.randrange(len(maxMovesArray))

            #Commit this random move.
            board.push(maxMovesArray[randomIndex])
  
    def defendingRollout(self, board):
        #Out of all the current legal moves, filter for moves that would take a piece out of danger. 
        #After finding the moves that could save on your pieces from capture, find the move that 
        #saves the piece of maximum value. 

        #This implementation ensures that move will not take the piece into immediate danger.  
        #If there are no defensive moves to take, uses random rollout. 
        #board: The representation of the current game board. 
        
        legalMoves = board.legal_moves
        defensiveMoves = []
        maxVal = 0
        
        #Iterating over all legal moves.
        for move in legalMoves:
            #Defining where the move starts and ends.
            landingSquare = move.to_square
            startingSquare = move.from_square

            #Ensuring we move from danger, to safety.
            if board.is_attacked_by(not board.turn, startingSquare) and not board.is_attacked_by(not board.turn, landingSquare):
                #Getting the value for the piece we are considering "saving".
                pieceVal = board.piece_type_at(startingSquare)

                if pieceVal > maxVal:
                    defensiveMoves = []
                    maxVal = pieceVal
                    defensiveMoves.append(move)

                elif pieceVal == maxVal:
                    defensiveMoves.append(move)

        #If there are no such defensive moves, use random rollout.
        if len(defensiveMoves) == 0:
            self.randomRollout(board)

        elif len(defensiveMoves) == 1:
            #If there is 1 clear best move, commit to it. 
            board.push(defensiveMoves[0])

        else:
            #Pick a random move out of the best possible.
            random_index = random.randrange(len(defensiveMoves))
      
            #Commit this random move. 
            board.push(defensiveMoves[random_index])

    def simulation(self):
        #Rollout to then end of the game. Utilizes a rollout strategy to make decisions. 

        board = copy.deepcopy(self.state)
        totalMoves = 0

        #Loop until the game is over, or we break out after 80 moves.
        while not board.is_game_over():
            totalMoves += 1
       
            #Delegate to the proper rollout strategy. 
            if self.rolloutStrategy == "random":
                self.randomRollout(board)

            elif self.rolloutStrategy == "attacking":
                self.attackingRollout(board)

            elif self.rolloutStrategy == "defending":
                self.defendingRollout(board)

            #If we have hit the max number of moves, end the simulation to move onto next. 
            if totalMoves >= 80:
                break

        #If the number of moves is greater than 80, cancel this simulation.
        if totalMoves >= 80:
            #Using helper heuristic to evaluate the board state.
            outcome = calculateBoardValue(board)
            
            if outcome > 0:
                winner = True #WHITE wins 
            
            elif outcome < 0:
                winner = False #BLACK wins 

            elif outcome == 0:
                winner = None #TIE 

        else:
            outcome = board.result()
            
            #If the result is a tie:
            if str.startswith(outcome, "1/2"):
                winner = None
            
            #Win
            elif outcome == "1-0":
                winner = True 
            
            #Loss
            elif outcome == "0-1":
                winner = False 
        
        #Use backpropogation so we can "learn" from the previous simulation.
        self.backpropagation(winner)

    def backpropagation(self, winner):
        #Traverses up the MCTS Tree from a leaf.
        #winner: a number representing if white or black won the simulation. Or None if it was a tie.  
        
        #white = 1, black = 0 
        if winner is None:
            self.ties += 1
    
        elif winner == self.color:
            self.wins += 1
    
        else:
            self.losses += 1
    
        #Recursive case 
        if self.parent is not None:
            self.parent.backpropagation(winner)

    def ucb1(self, successRate, c, totalTimesExplored, timesExplored):
        result = successRate + c * (sqrt((2 * log(totalTimesExplored)) / timesExplored))
        return result