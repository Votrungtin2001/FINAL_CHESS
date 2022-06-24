from tkinter import Tk, Button
from game import Game

mode = ""

#Set up Window
window = Tk()
window.title("Please select a mode before starting a match!")

#Set up 4 options before playing
humanHuman = Button(window, width = 30, height = 15, text = "Human x Human", bg = "#32a88d", font='sans 10 bold', fg="white", command = lambda: startGame("humanHuman"))
humanMinimax = Button(window, width = 30, height = 15, text = "Human x CPU (Minimax Algorithm)", bg = "#85d665", font='sans 10 bold', fg="white", command = lambda: startGame("humanMinimax"))
humanMCTS = Button(window, width = 30, height = 15, text = "Human - CPU (MCTS Algorithm)", bg = "#e63232", font='sans 10 bold', fg="white", command = lambda: startGame("humanMCTS"))
mctsMinimax = Button(window, width = 30, height = 15, text = "Computer (MCTS) - CPU (Minimax)", bg = "#eba94d", font='sans 10 bold', fg="white", command = lambda: startGame("mctsMinimax"))
humanHuman.grid(padx=5)
humanMinimax.grid(row = 0, column = 1)
humanMCTS.grid(pady=10)
mctsMinimax.grid(row = 1, column = 1, padx=5)

def startGame(Mode):
    global mode
    window.destroy()
    mode = Mode

# Finalize window
window.mainloop()

# Start game based on selected mode
if (mode != ""):
    if(mode == "humanHuman"):
        selectedMode = 'Human x Human. \nPlayer 1 (White - will move first): Human. \nPlayer 2 (Black): Human.'
    elif(mode == "humanMinimax"):
        selectedMode = 'Human x Computer (Minimax Algorithm). \nPlayer 1 (White - will move first): Human. \nPlayer 2 (Black): CPU(Minimax).'
    elif(mode == "humanMCTS"):
        selectedMode = 'Human x Computer (Monte Carlo Tree Search Algorithm). \nPlayer 1 (White - will move first): Human. \nPlayer 2 (Black): CPU(Monte Carlo Tree Search).'
    elif(mode == "mctsMinimax"):
        selectedMode = 'Computer (Monte Carlo Tree Search Algorithm) x Computer (Minimax Algorithm).'
    print("Player selected mode: " + selectedMode)
    Game(mode)