#!/usr/bin/env python3
import pyautogui
import time
import sys
import math
from PIL import Image
from Solver import Solver
from Vision import Vision

pyautogui.FAILSAFE = True          # Allows exiting the program by going to the top left of screen
RETINA_DISPLAY = True              # Mitch has a macbook
SCREEN_COORDS = [0, 46, 730, 1290] # Mitch's COORDS
MENUBAR_HEIGHT = 44                # Mitch's menubar height

def enterWord(word, speed=0):
    # Move to the start of the word before selecting anything
    pyautogui.mouseUp()
    pyautogui.moveTo(word[0][0], word[0][1], speed)
    pyautogui.mouseDown()

    # Move over each letter
    for letter in word:
        pyautogui.mouseDown()
        pyautogui.moveTo(letter[0], letter[1], speed)
        pyautogui.mouseDown()

    # Release mouse up and move to empty location
    pyautogui.mouseUp()
    pyautogui.moveTo(0, SCREEN_COORDS[1], 0)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

vision = Vision(SCREEN_COORDS)

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

# Play the game!
while(True):
    # Ensure window has focus by clicking it
    pyautogui.click(0, SCREEN_COORDS[1], 3)

    # Wait for any transitions to finish
    time.sleep(1)

    # Get level state and word lengths required
    state, wordLengths = vision.getBoardState()
    width = int(math.sqrt(len(state)))
    print(state, wordLengths)

    # Check state is reasonable
    if width == 0 or len(wordLengths) == 0 or width ** 2 != len(state) or sum(wordLengths) != len(state):
        print('Invalid state, resetting')
        clickButton(*vision.AD_BUTTON)
        clickButton(*vision.RESET_BUTTON)
        continue

    # Generate solutions
    solver = Solver(wordLengths)
    solutions = solver.solveLevel([c.lower() for c in state], wordLengths)

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
    for solutionState in solutions:
        # Get mouse coordinates for solution and enter them
        for i,path in enumerate(solutionState.path):
            before = max([vision.getBoardRatio() for i in range(2)]) # TODO(mitch): fix this, it sometimes get 0.0
            enterWord([mouseGrid[i] for i in path])
            after = max([vision.getBoardRatio() for i in range(2)]) # TODO(mitch): fix this, it sometimes get 0.0
            print(before)
            print(after)

            word = ('').join([solutionState.allStates[i][j] for j in path])

            # if the same ratio, the word entered was a bad one, so remove it from all solutions
            if round(before, 2) == round(after, 2):
                print('adding bad word,', word)
                solver.addBadWord(word)
                break

        # Else if no break, all words in solution were entered, exit out of entering solutions
        else:
            break

        # A problem occured, reset!
        clickButton(*vision.RESET_BUTTON)
