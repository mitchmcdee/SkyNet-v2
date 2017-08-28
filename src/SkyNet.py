import pyautogui
import time
import sys
import math
from PIL import Image
from searchTrie import solveLevel
from Vision import Vision

pyautogui.FAILSAFE = True
RETINA_DISPLAY = True
SCREEN_COORDS = [0, 46, 730, 1290]      # Mitch's COORDS

def screenshot(left, top, right, bottom):
    width = right - left
    height = bottom - top
    return pyautogui.screenshot(region=(left, top, width, height))

def enterWord(word, speed = 0.15):
    # Move to the start of the word before selecting anything
    pyautogui.moveTo(word[0][0], word[0][1], speed)
    pyautogui.mouseDown()

    # Move over each letter
    for letter in word:
        pyautogui.mouseDown()
        pyautogui.moveTo(letter[0], letter[1], speed)
        pyautogui.mouseDown()

    # Release mouse up, move to empty location and sleep for a bit while blocks fall into place
    pyautogui.mouseUp()
    pyautogui.moveTo(500, 500, 0)
    time.sleep(1)

# Play the game!
while(True):
    # Get level state, coords and word lengths required
    vision = Vision(SCREEN_COORDS)
    state, wordLengths = vision.getBoardState()
    print(state, wordLengths)

    # Generate solutions
    solutions = solveLevel([c.lower() for c in state], wordLengths)

    # Generate mouse grid
    width = int(math.sqrt(len(state)))
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
            before = vision.getScreenRatio()
            enterWord([mouseGrid[i] for i in word])
            after = vision.getScreenRatio()

            # if the same ratio, the word entered was a bad one, so remove it from all solutions
            if before == after:
                failed = True
                solutions = [s for s in solutions if word not in s]
                break

        # Sleep and check if we've won
        time.sleep(2)
        if not failed and vision.checkLevelComplete():
            # Sleep while we wait for game to be over
            time.sleep(3)
            break

        # Click the reset button
        reset = vision.RESET_BUTTON
        resetWidth = reset[0] * vision.width
        resetHeight = reset[1] * vision.height

        # if on retina display, halve the mouse resolution due to scaling
        if RETINA_DISPLAY:
            resetWidth /= 2
            resetHeight /= 2

        pyautogui.moveTo(resetWidth, resetHeight)
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        time.sleep(2)
