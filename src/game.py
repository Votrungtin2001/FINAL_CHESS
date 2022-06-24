import chess
from tkinter import Tk
import gui

import computer
import time as timer


class Game:
    playerTurns = [True]#white always moves first when starting the match, 
                        #when in mctsMinimax mode, True means mcts plays as white, False means minimax plays as white
    
    isWhitePlayer = playerTurns[-1] #True means white, False means black
    defaultTurnForAI = True #True means white, False means black

    turnMCTS = 0
    turnMinimax = 0
    timeMinimax = []
    timeMCTS = []

    #Check whether it is repeated many times
    repeatedMCTSMove = []
    countRepeatedMCTSMove = []
    repeatedMinimaxMove = []
    countRepeatedMinimaxMove = []
    allMCTSMoves = []
    allMinimaxMoves = []

    #currentFilePath = "D:/NAM 3/HKII/CS106/FINAL PROJECT/FINAL_CHESS/result/"

    #Result.txt is output of this test case. 
    #Open for reading and appending (writing at end of file). The file is created if it does not exist.
    #a = open(currentFilePath + "result10.txt", "a+") 
    
    def __init__(self, Mode):
        self.mode = Mode
        self.board = chess.Board() #initial board
        self.turn = 0 

        #Default Mode
        self.humanHuman = False
        self.humanMinimax = False
        self.humanMCTS = False
        self.mctsMinimax = False
        self.isMCTS = False

        #Set up GUI
        self.setupWindow()
        self.display = gui.GUI(self.root, self, self.board, self.playerTurns, self.mode)
        self.display.pack(
            side='top', fill='both', expand='true', padx=4, pady=4)

        #For pawn upgrade
        self.whiteWindowOpened = False
        self.blackWindowOpened = False

        #Start
        self.start()

    def setupWindow(self):
        self.root = Tk() 
        if(self.mode == "humanHuman"):
            title = 'Human x Human'
            self.humanHuman = True
            self.humanMinimax = False
            self.humanMCTS = False
            self.mctsMinimax = False
            self.isMCTS = False

        elif(self.mode == "humanMinimax"):
            title = 'Human x Computer (Minimax Algorithm)'
            self.humanHuman = False
            self.humanMinimax = True
            self.humanMCTS = False
            self.mctsMinimax = False
            self.isMCTS = False

        elif(self.mode == "humanMCTS"):
            title = 'Human x Computer'
            self.humanHuman = False
            self.humanMinimax = False
            self.humanMCTS = True
            self.mctsMinimax = False
            self.isMCTS = False

        elif(self.mode == "mctsMinimax"):
            title = 'Computer (Monte Carlo Tree Search Algorithm) x Computer (Minimax Algorithm)'
            self.humanHuman = False
            self.humanMinimax = False
            self.humanMCTS = False
            self.mctsMinimax = True

            if(self.isWhitePlayer == True): self.isMCTS = True
            else: self.isMCTS = False

        self.root.title(title)
        self.root.geometry("525x540")

    def start(self):
        if (self.isWhitePlayer == True):
            if(self.mctsMinimax == True):
                self.display.label_status["text"] = "White will move first. Waiting for the first action from CPU(MCTS)..."
                self.isMCTS = True
                self.root.after(1500, self.computerPlay)

            else:
                self.display.label_status["text"] = "White will move first. Waiting for the first action from Player 1..."

                self.root.after(1500, self.playerPlay)

        else:
            if(self.mctsMinimax == True):
                self.display.label_status["text"] = "White will move first. Waiting for the first action from CPU(Minimax)..."
                self.isMCTS = False
                self.root.after(1500, self.computerPlay)

            else:
                self.display.label_status["text"] = "White will move first. Waiting for the first action from Player 1..."
                self.root.after(1500, self.playerPlay)

        self.root.mainloop()

    def playerPlay(self):
        playerTurn = self.playerTurns[-1]
        if(playerTurn == True and self.mode != "mctsMinimax"):
            self.display.label_status['text'] = "Player 1's turn - White. Waiting for the new action from Player 1..."
        elif(playerTurn == False and self.mode == "humanHuman"):
            self.display.label_status['text'] = "Player 2's turn - Black. Waiting for the new action from Player 2..."
        else: 
            self.root.after(100000000, self.computerPlay)
        
        
    def computerPlay(self):
        #In order to see clearly the move
        timer.sleep(2)

        #Save record
        if(self.mode == "mctsMinimax"):
            if(self.isMCTS == True):
                self.turnMCTS+=1
                mctsStart = timer.time()
            else:
                self.turnMinimax+=1 
                minimaxStart = timer.time()

        computer.Computer(self.board, self.isWhitePlayer, self.mode, self.isMCTS).aiMove(self.turnMCTS, self.repeatedMCTSMove, self.repeatedMinimaxMove, self.countRepeatedMCTSMove, self.countRepeatedMinimaxMove, self.turnMCTS, self.turnMinimax, self.allMCTSMoves, self.allMinimaxMoves)
        
        #Check whether it is repeated move
        if(len(self.countRepeatedMCTSMove) >= 3):
            self.countRepeatedMCTSMove = []
            self.repeatedMCTSMove = []
            self.repeatedMCTSMove.append(self.allMCTSMoves[-1])
        if(len(self.countRepeatedMinimaxMove) >= 3):
            self.countRepeatedMinimaxMove = []
            self.repeatedMinimaxMove = []
            self.repeatedMinimaxMove.append(self.allMinimaxMoves[-1])
        
        #Save record
        if(self.mode == "mctsMinimax"):
            if(self.isMCTS == True):
                mctsEnd = timer.time()
                self.timeMCTS.append(mctsEnd - mctsStart)

            else: 
                minimaxEnd = timer.time()
                self.timeMinimax.append(minimaxEnd - minimaxStart)


        

        self.isMCTS = not self.isMCTS
        

        self.display.refresh()
        self.display.drawPieces()

        if(self.playerTurns[-1] == True): self.playerTurns.append(False)
        else: self.playerTurns.append(True)

        if self.board.is_checkmate():
            if(self.playerTurns[-1] == True): 
                text = "Checkmate. Black won."
                resultMatch = "Black won"
            else: 
                text = "Checkmate. White won"
                resultMatch = "White won"
            self.display.label_status['text'] = text

            #Save record
            if(self.mode == "mctsMinimax"):
                print("Save record")
                #self.a.write("Test No. 10:")
                #self.a.write('\n')

                #Minimax
                #self.a.write('\n')
                #self.a.write("Minimax: ")
                #self.a.write('\n')
                totalTurn = str('\tTotal turn: '+ str(self.turnMinimax))
                #self.a.write(totalTurn)
                #self.a.write('\n')
                time = str('\tTime: '+ str(self.timeMinimax))
                #self.a.write(time)
                #self.a.write('\n')
                totalTime = 0

                totalTimeMatch = 0

                for time in self.timeMinimax:
                    totalTime+=time 
                averageTime = str('\tAverage time for each move: '+ str(totalTime/self.turnMinimax))
                #self.a.write(averageTime)
                #self.a.write('\n')

                totalTimeMatch += totalTime

                #MCTS
                #self.a.write('\n')
                #self.a.write("MCTS: ")
                #self.a.write('\n')
                totalTurn = str('\tTotal turn: '+ str(self.turnMCTS))
                #self.a.write(totalTurn)
                #self.a.write('\n')
                time = str('\tTime: '+ str(self.timeMCTS))
                #self.a.write(time)
                #self.a.write('\n')
                totalTime = 0
                for time in self.timeMCTS:
                    totalTime+=time 

                totalTimeMatch += totalTime
                
                averageTime = str('\tAverage time for each move: '+ str(totalTime/self.turnMCTS))
                #self.a.write(averageTime)
                #self.a.write('\n')

                #self.a.write('\n')
                totalTimeMatchStr = str('Total time of a match: '+ str(totalTimeMatch))
                #self.a.write(totalTimeMatchStr)
                #self.a.write('\n')
                
                #self.a.write('\n')
                #self.a.write('Result: ' + str(resultMatch))
                #self.a.write('\n')


                #self.a.close()

        elif self.board.is_stalemate():
            self.display.label_status['text'] = "It was a draw match."

             #Save record
            if(self.mode == "mctsMinimax"):
                print("Save record")
                #self.a.write("Test No. 10:")
                #self.a.write('\n')

                #Minimax
                #self.a.write('\n')
                #self.a.write("Minimax: ")
                #self.a.write('\n')
                totalTurn = str('\tTotal turn: '+ str(self.turnMinimax))
                #self.a.write(totalTurn)
                #self.a.write('\n')
                time = str('\tTime: '+ str(self.timeMinimax))
                #self.a.write(time)
                #self.a.write('\n')
                totalTime = 0
                totalTimeMatch = 0
                
                for time in self.timeMinimax:
                    totalTime+=time 

                totalTimeMatch += totalTime

                averageTime = str('\tAverage time for each move: '+ str(totalTime/self.turnMinimax))
                #self.a.write(averageTime)
                #self.a.write('\n')

                #MCTS
                #self.a.write('\n')
                #self.a.write("MCTS: ")
                #self.a.write('\n')
                totalTurn = str('\tTotal turn: '+ str(self.turnMCTS))
                #self.a.write(totalTurn)
                #self.a.write('\n')
                time = str('\tTime: '+ str(self.timeMCTS))
                #self.a.write(time)
                #self.a.write('\n')
                totalTime = 0
                for time in self.timeMCTS:
                    totalTime+=time 

                totalTimeMatch += totalTime

                averageTime = str('\tAverage time for each move: '+ str(totalTime/self.turnMCTS))
                #self.a.write(averageTime)
                #self.a.write('\n')

                #self.a.write('\n')
                totalTimeMatchStr = str('Total time of a match: '+ str(totalTimeMatch))
                #self.a.write(totalTimeMatchStr)
                #self.a.write('\n')

                #self.a.write('\n')
                #self.a.write('Result: Draw')
                #self.a.write('\n')

                #self.a.close()

        else:
            playerTurn = self.playerTurns[-1]
            if(playerTurn == True and self.mode != "mctsMinimax"):
                self.root.after(100, self.playerPlay)
            elif(playerTurn == False and self.mode == "humanHuman"):
                self.root.after(100, self.playerPlay)
            else:
                if(self.mode == "mctsMinimax"):
                    if(self.isWhitePlayer == True):
                        if(self.isMCTS == True):
                            self.display.label_status['text'] = "CPU(MCTS)'s turn - White. The computer is thinking..."
                        else: self.display.label_status['text'] = "CPU(Minimax)'s turn - Black. The computer is thinking..."
                    else:
                        if(self.isMCTS == True):
                            self.display.label_status['text'] = "CPU(MCTS)'s turn - Black. The computer is thinking..."
                        else: self.display.label_status['text'] = "CPU(Minimax)'s turn - White. The computer is thinking..."
                    
                elif(playerTurn == False and self.mode != "mctsMinimax" and self.mode != "humanHuman"):
                    self.display.label_status['text'] = "Computer's turn - Black. The computer is thinking..."
                
                self.root.after(100, self.computerPlay)

