from cmath import inf
import pickle

from chess.polyglot import open_reader
import chess
from random import randint
from backup.computer1 import expansion
from board import evaluateBoard, calculate_board_value
import random
import copy
import math
import numpy as np

class Computer:
    #For minimax algorithm
    depth = 3
    board_caches = {}
    cache_hit = 0
    cache_miss = 0

    #For MCTS algorithm
    rollout_strategy = "defending" 
    #rollout_strategy = "attacking" 
    simulations = 200 
    show_node_results = True

    #Set up cache 
    try:
        cache = open('data/cache.p', 'rb')
    except IOError:
        #Create new file cache.p when it is not existed
        cache = open('data/cache.p', 'wb')
        pickle.dump(board_caches, cache)
    else:
        #Load cache when it existed
        board_caches = pickle.load(cache)

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

        self.isWhitePlayer = not isWhitePlayer
        self.isMCTS = isMCTS

        with open_reader('data/opening.bin') as reader:
            self.opening_moves = [
                str(entry.move) for entry in reader.find_all(board)
            ]

    def minimaxMove(self):
        global_score = -1e8 if self.isWhitePlayer else 1e8
        chosen_move = None

        #Can move from opening book
        if self.opening_moves:
            chosen_move = chess.Move.from_uci(
                self.opening_moves[randint(0, len(self.opening_moves) // 2)])
        else:
            for move in self.board.legal_moves:
                self.board.push(move)

                local_score = self.minimax(self.depth - 1, not self.isWhitePlayer,
                                           -1e8, 1e8)

                self.board_caches[self.hashBoard(
                    self.depth - 1, not self.isWhitePlayer)] = local_score

                if self.isWhitePlayer and local_score > global_score:
                    global_score = local_score
                    chosen_move = move
                elif not self.isWhitePlayer and local_score < global_score:
                    global_score = local_score
                    chosen_move = move

                self.board.pop()
                print(local_score, move)

            print('\ncache_hit: ' + str(self.cache_hit))
            print('cache_miss: ' + str(self.cache_miss) + '\n')

        print(str(global_score) + ' ' + str(chosen_move) + '\n')

        self.board.push(chosen_move)

        with open('data/cache.p', 'wb') as cache:
            pickle.dump(self.board_caches, cache)

    def aiMove(self):
        if(self.mode == "humanMinimax"):
            if(self.isWhitePlayer == False):
                print('minimax')
                self.minimaxMove()

        elif(self.mode == "mctsMinimax"):
            if(self.isMCTS == False):
                print('minimax')
                self.minimaxMove()
            else:
                print('mcts')
                self.MCTSMove()

        elif(self.mode == "humanMCTS"):
            if(self.isWhitePlayer == False):
                print('mcts')
                self.MCTSMove()



    def minimax(self, depth, isMaxingWhite, alpha, beta):
        #If board in cache
        if self.hashBoard(depth, isMaxingWhite) in self.board_caches:
            self.cache_hit += 1

            return self.board_caches[self.hashBoard(depth, isMaxingWhite)]

        self.cache_miss += 1

        # if depth is 0 or game is over
        if depth == 0 or not self.board.legal_moves:
            self.board_caches[self.hashBoard(
                depth, isMaxingWhite)] = evaluateBoard(self.board)
            return self.board_caches[self.hashBoard(depth, isMaxingWhite)]

        # else
        best_score = -1e8 if isMaxingWhite else 1e8
        for move in self.board.legal_moves:
            self.board.push(move)

            local_score = self.minimax(depth - 1, not isMaxingWhite, alpha,
                                       beta)
            self.board_caches[self.hashBoard(
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
        self.board_caches[self.hashBoard(depth, isMaxingWhite)] = best_score
        return self.board_caches[self.hashBoard(depth, isMaxingWhite)]

    def hashBoard(self, depth, isMaxingWhite):
        return str(self.board) + ' ' + str(depth) + ' ' + str(isMaxingWhite)

    def MCTSMove(self):
        root = MCTS_Node(self.board, not self.isMCTS)
        move = root.best_action(self.simulations, 0.1)

        #Finding the best child node
        
        #Updating the board then returning 
        self.board.push(move)

class MonteCarloTreeSearchNode:

    def __init__(self, state, parent, parent_action, rollout_strategy, color):
        #Represents a node for usage in MCTS algorithm.

        #state: The board object representing the state of the game. 
        #parent: The Node object this node was derived from. None for root node. 
        #parent_action: The action taken by parent Node to get to this state. None for root node. 
        #rollout_strategy (String): Represents which strategy to use for rollouts to end of game.  
   
        #State is a chess.Board: The board to play the player's move on.
        self.state = state 
        #Reference to the parent Node. 
        self.parent = parent 
        #The move taken to arrive at this state from the parent Node. 
        self.parent_action = parent_action
        #Defining an empty list of children Nodes. 
        self.children = []
        #Number of simulations won/lost/tied from this Node. 
        self.wins, self.losses, self.ties = 0, 0, 0 
        #Setting the rollout strategy for this MCTS algorithm
        self.rollout_strategy = rollout_strategy
        #Sets which color this AI is playing as
        self.color = color

    def pick_move(self, legal_moves):
        #Picks a random, untaken move from this Node.  
        #legal_moves: list of Move objects. 
        #Returns: A single Move object that does not have a Node built for it yet.  

        #List of all actions taken by the current children of this Node. 
        child_actions_taken = []

        for child in self.children:
            #Looking at children's parent_action field. 
            child_actions_taken.append(child.parent_action)

        #Moves that have not been taken yet 
        untaken_moves = []
    
        for move in legal_moves:
            #Making sure the move has not been taken by a child of this Node.
            if move not in child_actions_taken:
                untaken_moves.append(move)
    
        rand_index = random.randrange(len(untaken_moves))
        rand_move = untaken_moves[rand_index]
        return rand_move

    def selection(self):
        #Select a child node in the tree. If all children have been explored, 
        #use the UCB1 formula. Otherwise, expand a random child node. 
        
        if self.state.legal_moves.count() == 0:
            return 

        #Do the selection
        if self.state.legal_moves.count() == len(self.children):        
            #We chose to set c as sqrt(2). Does a good job of balancing exploration and exploitation.
            c = 1.414 #sqrt(2)

            #Get the total number of times we've explored any children.
            total_times_explored = self.wins + self.ties + self.losses

            #Calculate all of the ucb1 scores for each node.
            scores = []
            for node in self.children:
                times_explored = node.wins + node.ties + node.losses
                success_rate = (node.wins + (node.ties / 2)) / times_explored
                ucb1 = success_rate + c * (math.sqrt((2 * math.log(total_times_explored)) / times_explored))
                scores.append(ucb1)
      
            #Get the node which has the highest ucb1 score.
            selection_index = scores.index(max(scores))
            selection_node = self.children[selection_index]

            #Recursively perform selection on the child node we select.
            selection_node.selection()

        else:
            #Do the expansion 
            self.expansion()

    def expansion(self):
        #Take a random unexplored move, and create a Node for that next state.
        
        #Pick a random move.
        new_move = self.pick_move(self.state.legal_moves)
        
        #Copying the board
        board_copy = copy.deepcopy(self.state)
        board_copy.push(new_move)
        new_board = board_copy
    
        #Pick a legal move that doesn't have a Node yet.
        #Creating a new node with self as the parent. 
        newNode = MonteCarloTreeSearchNode(new_board, self, new_move, self.rollout_strategy, self.color)
        
        #Do simulation on the new node.
        newNode.simulation()

        #Adding the new node to the children of the parent node.
        self.children.append(newNode)

    def random_rollout(self, board):
        #Responsible for picking an available move and doing board.push(move). 
        #In this case, the move is completely random for the random rollout strategy. 
        #board: The representation of the current game board. 

        #Getting a random move from all valid moves.
        legal_moves = board.legal_moves
        random_move = random.randrange(legal_moves.count())

        i = 0
        for move in legal_moves:
            if i == random_move:
                #Updating the board.
                board.push(move)
                break

            i += 1

    def attacking_rollout(self, board):
        #Out of all the current legal moves, filter for moves that take enemy pieces. 
        #Then find the move with the max value, defined by the piece_values function above. 
        #This is a fairly common heuristic in chess. Where taking more important pieces result in higher rewards. 
        #If there are no attacking moves to play, use random rollout. 
        #board: The representation of the current game board.
         
        legal_moves = board.legal_moves
        max_val = 0
        max_moves_array = []

        for move in legal_moves:
            #Checking where the move lands the piece in question.
            landing_square = move.to_square

            #Checking if the position already has an enemy piece, this represents taking a piece.  
            #piece_val is a number
            piece_val = board.piece_type_at(landing_square)
            
            #If move is attacking an opponent piece:
            if piece_val is not None:
                #If this is the new max move, update.
                if piece_val > max_val:
                    #This is a new high score, need a new moves array.
                    max_moves_array = []
                    max_val = piece_val
                    max_moves_array.append(move) 
                elif piece_val == max_val:
                    #This is tie for high score, add to the existing array.
                    max_moves_array.append(move)
    
        #If there is no max move, use random rollout.
        if len(max_moves_array) == 0:
            self.random_rollout(board)

        elif len(max_moves_array) == 1:
            #If there is 1 clear best move, commit to it. 
            board.push(max_moves_array[0])
        
        else:
            #Pick a random move out of the best possible.
            random_index = random.randrange(len(max_moves_array))

            #Commit this random move.
            board.push(max_moves_array[random_index])
  
    def defending_rollout(self, board):
        #Out of all the current legal moves, filter for moves that would take a piece out of danger. 
        #After finding the moves that could save on eof your pieces from capture, find the move that 
        #saves the piece of maximum value. 

        #This implementation ensures that move will not take the piece into imediate danger.  
        #If there are no defensive moves to take, uses random rollout. 
        #board: The representation of the current game board. 
        
        legal_moves = board.legal_moves
        defensive_moves = []
        max_val = 0
        
        #Iterating over all legal moves.
        for move in legal_moves:
            #Defining where the move starts and ends.
            landing_square = move.to_square
            starting_square = move.from_square

            #Ensuring we move from danger, to safety.
            if board.is_attacked_by(not board.turn, starting_square) and not board.is_attacked_by(not board.turn, landing_square):
                #Getting the value for the piece we are considering "saving".
                piece_val = board.piece_type_at(starting_square)

                if piece_val > max_val:
                    defensive_moves = []
                    max_val = piece_val
                    defensive_moves.append(move)

                elif piece_val == max_val:
                    defensive_moves.append(move)

        #If there are no such defensive moves, use random rollout.
        if len(defensive_moves) == 0:
            self.random_rollout(board)

        elif len(defensive_moves) == 1:
            #If there is 1 clear best move, commit to it. 
            board.push(defensive_moves[0])

        else:
            #Pick a random move out of the best possible.
            random_index = random.randrange(len(defensive_moves))
      
            #Commit this random move. 
            board.push(defensive_moves[random_index])

    def simulation(self):
        #Rollout to then end of the game. Utilizes a rollout strategy to make decisions. 

        board = copy.deepcopy(self.state)
        turn = board.turn
        total_moves = 0

        #Loop until the game is over, or we break out after 80 moves.
        while not board.is_game_over():
            total_moves += 1
       
            #Delegate to the proper rollout strategy. 
            if self.rollout_strategy == "random":
                self.random_rollout(board)

            elif self.rollout_strategy == "attacking":
                self.attacking_rollout(board)

            elif self.rollout_strategy == "defending":
                self.defending_rollout(board)

            #If we have hit the max number of moves, end the simulation to move onto next. 
            if total_moves >= 80:
                break

        #If the number of moves is greater than 80, cancel this simulation.
        if total_moves >= 80:
            #Using helper heuristic to evaluate the board state.
            outcome = calculate_board_value(board)
            
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

def get_legal_moves(board):
    #Returns the list of legal moves from the current board position
    #board : The current board state

    return list(board.legal_moves)


class MCTS_Node():
    def __init__(self, board, color, parent=None, parent_action=None):
        #board : The board state
        #color : str - The player's color (black, white)
        #parent : Node, optional - The parent of the current node, by default None
        #parent_action : Move, optional - The action that the parent carried out, by default None

        self.board = copy.deepcopy(board)
        self.color = color
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._reward = 0
        self._untried_actions = get_legal_moves(self.board)

    def expand(self):
        #Expands the current node with an untried action
        random.shuffle(self._untried_actions)
        action = self._untried_actions.pop()

        next_state = copy.deepcopy(self.board)
        next_state.push(action)

        child_node = MCTS_Node(next_state, color=self.color, parent=self, parent_action=action)
        self.children.append(child_node)

        return child_node

    def simulate(self):
        #From the current state simulate the game untill there is an outcome for the game
        simulation_state = copy.deepcopy(self.board)

        while not simulation_state.is_game_over():

            possible_moves = get_legal_moves(simulation_state)

            action = self.simulation_policy(possible_moves)
            simulation_state.push(action)
        out = simulation_state.outcome().result()

        if out == "1/2-1/2":
            return 0.5
        elif self.color == 'white' and out == "1-0" or self.color == 'black' and out == "0-1":
            return 1
        else:
            return 0

    def backpropagate(self, result):
        #Backpropagate the results
        self._number_of_visits += 1.
        self._reward += result
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, c=0.1):
        #Select the best child
        weights = []
        for child in self.children:
            exploitation = self._reward / self._number_of_visits
            exploration = c * np.sqrt((2 * np.log(self._number_of_visits) / child._number_of_visits))
            ucb = exploration + exploitation

            weights.append(ucb)

        return self.children[np.argmax(weights)]


    def simulation_policy(self, possible_moves):
        #The policy to select the next move in the simulation step.
        #It implements a uniform sampling among possible moves.
        
        return possible_moves[random.randrange(len(possible_moves))]

    def _tree_policy(self):
        #Select a node to run the simulation
        current_node = self
        while not current_node.board.is_game_over():
            if current_node._untried_actions:
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node


    def best_action(self, n_simulations, c):
        #Select the node corresponding to the best action
        for i in range(n_simulations):
            v = self._tree_policy()
            reward = v.simulate()
            v.backpropagate(reward)

        return self.best_child(c=c).parent_action

    
    def selection(current_node):
        max_ucb = -inf
        selected_child = None
        for i in current_node.children:
            current_ucb = ucb_value(i)
            if(current_ucb > max_ucb):
                max_ucb = current_ucb
                selected_child = i
        return (selected_child)

    def expansion(current_node):
        if(current_node.children.empty()):
            return current_node #leaf node reached
        max_ucb = -inf
        selected_child = None
        for i in current_node.children:
            current_ucb = ucb_value(i)
            if(current_ucb > max_ucb):
                max_ucb = current_ucb
                selected_child = i
        return expansion(selected_child)

    


def ucb_value(self, i):
        #Select the node corresponding to the best action
        return 1

def generate_all_states(self, i):
        #Select the node corresponding to the best action
        return 1

won = 1
lose = 2


def simulation(current_node):
        if(current_node.game_over()):
            if(won):
                return (1, current_node)
            elif(lose):
                return (-1, current_node)
            else: 
                return (0.5, current_node)

        current_node.children = generate_all_states(current_node)
        random_child = random.choice(current_node.children)
        return simulation(random_child)

def backpropogation(current_node, reward):
        while(current_node.parent != None):
           #v means the number of times 
           #when this node is visited
           current_node.v += reward 
           current_node = current_node.parent
        return current_node