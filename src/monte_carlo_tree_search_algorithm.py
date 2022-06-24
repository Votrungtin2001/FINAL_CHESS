from monte_carlo_tree_search_node import MonteCarloTreeSearchNode as Node
import random

class MCTSAlgorithm:
    #For MCTS algorithm
    rolloutStrategy = "defending" 
    #rolloutStrategy = "attacking" 
    simulations = 1000
    showNodeResults = True

    def __init__(self, board, colorMCTS):
        self.board = board
        self.colorMCTS = colorMCTS

    def MCTSMove(self, repeatedMCTSMove, countRepeatedMCTSMove, turnMCTS, allMCTSMoves):
        #board (chess.Board): The board to play the AI's move on.
        #rollout_strategy (str): Represents which strategy to use for rollouts to end of game.  
        #show_node_results (bool): Display the wins and losses of each node.

        #Creating a Node with random rollout strategy 
        root = Node(self.board, None, None, self.rolloutStrategy, self.colorMCTS)

        #Running selection for a hardcoded amount of iterations 
        for i in range(self.simulations):
            root.selection()

        bestRecord = 0
        bestMoves = []
        childWinrate = 0

        if self.showNodeResults:
            print("Node move - wins - losses")

        #Traversing over the game_root's children nodes
        for child in root.children:
            childWinrate += child.wins
            childWinrate -= child.losses
      
            if self.showNodeResults:
                print(child.parentAction, child.wins, child.losses)
            
            if child.wins + child.losses == 0:
                record = 0.5
            else:
                record = child.wins / (child.wins + child.losses)
      
            if record > bestRecord:
                bestRecord = record
                bestMoves = []
                bestMoves.append(child)
      
            elif record == bestRecord:
                bestMoves.append(child)

        #Finding the best child node
        if(len(bestMoves) >= 2): bestNode = bestMoves[random.randrange(len(bestMoves))]
        elif(len(bestMoves) == 1): bestNode = bestMoves[0]

        #Handel when repeating move
        if(len(repeatedMCTSMove) > 0):
            if(len(allMCTSMoves) >= 3):
                repeatedMove = allMCTSMoves[-2]
                if(str(bestNode.parentAction) == str(repeatedMove)):
                    countRepeatedMCTSMove.append(1)
                    repeatedMCTSMove.append(bestNode.parentAction)

                if(len(countRepeatedMCTSMove) >= 3):
                    print("repeatedMCTS")
                    repeatedMove = repeatedMCTSMove[-1]
                    childWinrate = 0
                    bestRecord = 0
                    bestMoves = []

                    count = 0

                    for move in self.board.legal_moves:
                        count+=1

                    #Traversing over the game_root's children nodes
                    for child in root.children:
                        childWinrate += child.wins
                        childWinrate -= child.losses
      
                    if self.showNodeResults:
                        print(child.parentAction, child.wins, child.losses)
            
                    if child.wins + child.losses == 0:
                        record = 0.5
                    else:
                        record = child.wins / (child.wins + child.losses)
      
                    if record > bestRecord:
                        if(str(child.parentAction) != str(repeatedMove)):
                            bestRecord = record
                            bestMoves = []
                            bestMoves.append(child)
      
                    elif record == bestRecord:
                        if(str(child.parentAction) != str(repeatedMove)):
                            bestMoves.append(child)

                    if(len(bestMoves) >= 2): bestNode = bestMoves[random.randrange(len(bestMoves))]
                    elif(len(bestMoves) == 1): bestNode = bestMoves[0]

                    randomIndex = random.randint(0, count - 1)
                    count = 0
                    for move in self.board.legal_moves:
                        count+=1
                        if(randomIndex == count - 1):
                            bestNode.parentAction = move

        print("The selected move after running mcts algorithm:")
        print(str(bestNode.parentAction) + '\n')

        if(turnMCTS == 1): repeatedMCTSMove.append(bestNode.parentAction)
        allMCTSMoves.append(bestNode.parentAction)

        
        #Updating the board then returning 
        self.board.push(bestNode.parentAction)