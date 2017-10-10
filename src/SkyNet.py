#!/usr/bin/env python3
import pyautogui
import sys
import time
from math import sqrt
from PIL import Image
from Solver import Solver
from Vision import Vision
from Screen import Screen
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('solutions.log')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

pyautogui.FAILSAFE = True  # Allows exiting the program by going to the top left of screen
RETINA_DISPLAY = True  # Mitch has a macbook
SCREEN_COORDS = [0, 46, 730, 1290]  # Mitch's COORDS
MENUBAR_HEIGHT = 44  # Mitch's menubar height


# TODO(mitch): rewrite this as a class

def enterWord(word, speed=0):
    # board ratio before entering word
    start = vision.getBoardRatio()

    # Move over each letter
    pyautogui.mouseDown()
    for letter in word:
        pyautogui.moveTo(letter[0], letter[1], speed)
        pyautogui.mouseDown()

    # Release mouse and move to empty location
    pyautogui.mouseUp()
    pyautogui.moveTo(0, SCREEN_COORDS[1], speed)

    # Wait for animations to stop, necessary for computing board ratio
    time.sleep(0.6)

    # Return true if entered word was valid (board states were different), else false
    return start != vision.getBoardRatio()


# Click the button at the given relative width and height
def clickButton(widthPercentage, heightPercentage):
    w = widthPercentage * vision.width
    h = heightPercentage * vision.height

    # if on retina display, halve the mouse resolution due to scaling
    if RETINA_DISPLAY:
        w /= 2
        h /= 2

    pyautogui.moveTo(w, h)
    pyautogui.mouseDown()
    pyautogui.mouseUp()


def reset(sleepTime=0.0, screen=None):
    clickButton(*vision.AD_BUTTON)
    clickButton(*vision.RESET_BUTTON)
    clickButton(0, SCREEN_COORDS[1] / vision.height)
    time.sleep(sleepTime)


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
while True:
    # Set up output screen
    screen = Screen()

    logger.info('Getting board state')
    # Get level state and word lengths required
    state, wordLengths = vision.getBoardState()
    width = int(sqrt(len(state)))
    logger.info(f'{state} {wordLengths}')

    # width=1
    # wordLengths=[1]
    # state=list('h')

    # Check state is reasonable
    if width == 0 or width ** 2 != len(state) or len(state) != sum(wordLengths) or len(state) < 4:
        logger.info('Invalid state, resetting')
        reset(0.5)
        # Shut down screen
        screen.exit()
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

    # Keep track of time taking to generate solutions
    startTime = time.time()

    # Loop over valid solutions to try them all
    with Solver(state, wordLengths) as solver:
        for solution in solver.getSolutions():
            # Compute time it took to find a solution
            solutionTime = str(round(time.time() - startTime, 2))
            logger.info(f'{solutionTime}s - Entering: {solution.words}')

            # Get mouse coordinates for solution and enter them
            for i, path in enumerate(solution.path):
                isValid = enterWord([mouseGrid[i] for i in path])

                # TODO(mitch): detect when the thingo lagged out by testing for brown squares?

                # If the same ratio, the word entered was a bad one, so remove it from all solutions
                if not isValid:
                    badWord = ''.join([solution.allStates[i][j] for j in path])
                    solver.addBadWord(badWord)
                    break

            # Else if no break, all words in solution were entered, exit out of entering solutions
            else:
                if len(solution.words) == len(wordLengths):
                    break

            if i == 0 and not isValid:
                continue

            # A problem occurred, reset!
            reset(0.5)

        # Shut down screen
        screen.exit()
        time.sleep(0.5)
