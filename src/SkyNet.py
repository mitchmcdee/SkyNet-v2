#!/usr/bin/env python3
import pyautogui
import sys
import time
from math import sqrt
from PIL import Image
from Solver import Solver
from Vision import Vision

pyautogui.FAILSAFE = True          # Allows exiting the program by going to the top left of screen
RETINA_DISPLAY = True              # Mitch has a macbook
SCREEN_COORDS = [0, 46, 730, 1290] # Mitch's COORDS
MENUBAR_HEIGHT = 44                # Mitch's menubar height

def enterWord(word, speed=0):
    # board ratio before entering word
    before = vision.getBoardRatio()

    # Move over each letter
    pyautogui.mouseDown()
    for letter in word:
        pyautogui.moveTo(letter[0], letter[1], speed)
        pyautogui.mouseDown()

    # Release mouse and move to empty location
    pyautogui.mouseUp()
    pyautogui.moveTo(0, SCREEN_COORDS[1], speed)

    # Return true if entered word was valid (board states were different), else false
    return before != vision.getBoardRatio()

# Click the button at the given relative width and height
def clickButton(widthPercentage, heightPercentage):
    width = widthPercentage * vision.width
    height = heightPercentage * vision.height

    # if on retina display, halve the mouse resolution due to scaling
    if RETINA_DISPLAY:
        width /= 2
        height /= 2

    pyautogui.moveTo(width, height)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

def reset():
    clickButton(*vision.AD_BUTTON)
    clickButton(*vision.RESET_BUTTON)
    clickButton(0, SCREEN_COORDS[1] / vision.height)

################################################################################

# Set up computer vision
vision = Vision(SCREEN_COORDS)

# Wait for screen to become responsive (anrdoid emulator? osx? idek lol)
before = None
after = None
while before == after:
    before = vision.getBoardRatio()
    reset()
    after = vision.getBoardRatio()

# Play the game!
while(True):
    # Ensure window has focus by clicking it
    clickButton(0, SCREEN_COORDS[1] / vision.height)

    print('Getting board state')
    # Get level state and word lengths required
    state, wordLengths = vision.getBoardState()
    width = int(sqrt(len(state)))
    print(state, wordLengths)

    # width=6
    # wordLengths=[4,7,6]
    # state=list('____dw____ic____fo___tfa__spra__hiem')

    # Check state is reasonable
    if width == 0 or width ** 2 != len(state) or len(state) != sum(wordLengths):
        print('Invalid state, resetting')
        reset()
        continue

    # Generate mouse grid
    grid = Vision.GRID_CENTRES[width - 2]
    mouseGrid = []
    for j in range(width):
        for i in range(width):
            x = int((grid[0][0] + i * grid[1]) * vision.width)
            y = int((grid[0][1] + j * grid[2]) * vision.height) + MENUBAR_HEIGHT

            # if on retina display, halve the mouse resolution due to scaling
            if RETINA_DISPLAY:
                x /= 2
                y /= 2

            mouseGrid.append((x, y))

    # Loop over valid solutions to try them all
    with Solver(state, wordLengths) as solver:
        for solutionState in solver.getSolutions():
            # Get mouse coordinates for solution and enter them
            for i,path in enumerate(solutionState.path):
                isValid = enterWord([mouseGrid[i] for i in path])

                # TODO(mitch): detect when the thingo lagged out by testing for brown squares

                # If the same ratio, the word entered was a bad one, so remove it from all solutions
                if not isValid:
                    solver.addBadWord(('').join([solutionState.allStates[i][j] for j in path]))
                    break

            # Else if no break, all words in solution were entered, exit out of entering solutions
            else:
                break

            # A problem occured, reset!
            clickButton(*vision.RESET_BUTTON)
