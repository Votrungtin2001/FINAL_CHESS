


class Computer:
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


class node():
    def __init__(self):
        self.state = chess.Board()
        self.action = ''
        self.children = set()
        self.parent = None
        self.N = 0
        self.n = 0
        self.v = 0


def ucb1(current_node):
    ans = current_node.v + 2 * (sqrt(log(current_node.N + e + (10 ** -6)) / (current_node.n + (10 ** -10))))
    return ans


def rollout(current_node): # If the game is over return result else select a child node randomly.
    if current_node.state.is_game_over():
        board = current_node.state
        if board.result() == '1-0':
            return (1, current_node)
        elif board.result() == '0-1':
            return (-1, current_node)
        else:
            return (0.5, current_node)

    all_moves = [current_node.state.san(i) for i in list(current_node.state.legal_moves)]
    for i in all_moves:
        temp_state = chess.Board(current_node.state.fen())
        temp_state.push_san(i)
        child = node()
        child.state = temp_state
        child.parent = current_node
        current_node.children.add(child)
    random_state = random.choice(list(current_node.children))

    return rollout(random_state)


def expansion(current_node, isWhite): # selects the child node with max/min ucb value till we reach at leaf node
    if len(current_node.children) == 0:
        return current_node
    max_ucb = -inf
    if isWhite:
        max_ucb = -inf
        sel_child = None
        for i in current_node.children:
            tmp = ucb1(i)
            if (tmp > max_ucb):
                max_ucb = tmp
                sel_child = i

        return expansion(sel_child, 0)

    else:
        min_ucb = inf
        sel_child = None
        for i in current_node.children:
            tmp = ucb1(i)
            if (tmp < min_ucb):
                min_ucb = tmp
                sel_child = i

        return expansion(sel_child, 1)


def rollback(current_node, reward): # backpropagates till the root node. Updates reward and visited count of each node.
    current_node.n += 1
    current_node.v += reward
    while current_node.parent != None:
        current_node.N += 1
        current_node = current_node.parent
    return current_node


def mcts_pred(current_node, over, isWhite, iterations=10):
    if over:
        return -1
    all_moves = [current_node.state.san(i) for i in list(current_node.state.legal_moves)]
    map_state_move = dict()

    for i in all_moves:
        tmp_state = chess.Board(current_node.state.fen())
        tmp_state.push_san(i)
        child = node()
        child.state = tmp_state
        child.parent = current_node
        current_node.children.add(child)
        map_state_move[child] = i

    while iterations > 0:
        if isWhite: # White player tries to maximize the ucb value
            max_ucb = -inf
            sel_child = None
            for i in current_node.children:
                tmp = ucb1(i)
                if tmp > max_ucb:
                    max_ucb = tmp
                    sel_child = i
            ex_child = expansion(sel_child, 0)
            reward, state = rollout(ex_child)
            current_node = rollback(state, reward)
            iterations -= 1
        else: # Black player tries to minimize the ucb value
            min_ucb = inf
            sel_child = None
            for i in current_node.children:
                tmp = ucb1(i)
                if tmp < min_ucb:
                    min_ucb = tmp
                    sel_child = i

            ex_child = expansion(sel_child, 1)
            reward, state = rollout(ex_child)
            current_node = rollback(state, reward)
            iterations -= 1

    if isWhite:
        mx = -inf
        selected_move = ''
        for i in (current_node.children):
            tmp = ucb1(i)
            if (tmp > mx):
                mx = tmp
                selected_move = map_state_move[i]
        return selected_move
    else:
        mn = inf
        selected_move = ''
        for i in (current_node.children):
            tmp = ucb1(i)
            if (tmp < mn):
                mn = tmp
                selected_move = map_state_move[i]
        return selected_move

    def MCTSMove(self):
        root = node()
        root.state = self.board
        best_move = mcts_pred(root, self.board.is_game_over(), self.colorMCTS)
        
        #Updating the board then returning 
        self.board.push_san(best_move)