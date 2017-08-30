#!/usr/bin/env python3
import pyautogui
import time
import sys
import math
from PIL import Image
from Solver import Solver
from Vision import Vision

pyautogui.FAILSAFE = True
RETINA_DISPLAY = True
SCREEN_COORDS = [0, 46, 730, 1290]      # Mitch's COORDS

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
solver = Solver()

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
        clickButton(*vision.AD_BUTTON)
        clickButton(*vision.RESET_BUTTON)
        continue

    # Generate solutions
    solutions = solver.solveLevel([c.lower() for c in state], wordLengths)

    # Generate mouse grid
    grid = Vision.GRID_CENTRES[width - 2]
    mouseGrid = []
    for j in range(width):
        for i in range(width):
            x = int((grid[0][0] + i * grid[1]) * vision.width)
            y = int((grid[0][1] + j * grid[2]) * vision.height)

            # if on retina display, halve the mouse resolution due to scaling
            if RETINA_DISPLAY:
                x /= 2
                y /= 2

            mouseGrid.append((x, y))

    # Loop over valid solutions to try them all
    for i in range(len(solutions)):
        if i >= len(solutions):
            break

        failed = False
        # Get mouse coordinates for solution and enter them
        for word in solutions[i]:
            before = vision.getBoardRatio()
            enterWord([mouseGrid[i] for i in word])
            after = vision.getBoardRatio()

            # if the same ratio, the word entered was a bad one, so remove it from all solutions
            if round(before, 3) == round(after, 3):
                failed = True
                solutions = [s for s in solutions if [state[letter] for letter in word] not in [[state[l] for l in w] for w in s]]
                break

        # Check if failed
        if failed:
            clickButton(*vision.RESET_BUTTON)
            continue

        # Sleep and check if we've won
        time.sleep(1)
        if not failed and vision.checkLevelComplete():
            # Sleep while we wait for game to be over
            time.sleep(3.5)
            break

        # If we haven't won, click reset
        clickButton(*vision.RESET_BUTTON)
