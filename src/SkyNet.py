import pyautogui
import time
import sys
import math
from PIL import Image
from searchTrie import solveLevel
from cv import WordbrainCv
from cv_check import GameCompleteCV
from newCv import Vision

pyautogui.FAILSAFE = True

TESSERACT_PATH = '/usr/local/Cellar/tesseract/3.05.01/bin/tesseract'
SCREEN_COORDS = [0, 46, 730, 1290] # Mitch's COORDS

# for 2x2, 3x3, 4x4
GRID_COORDS = [[[94,218], [270,219], [94,393], [267,394]],
               [[65,193], [182,190], [299,190], [65,308], [182,309], [298,308], [67,421], [184,424], [299,425]],
               [[49,173], [141,177], [227,177], [317,175], [55,264], [139,263], [229,264], [314,263], [52,352], [140,352], [229,354], [315,353], [53,440], [139,439], [225,440], [315,442]]]

def screenshot(left, top, right, bottom):
    width = right - left
    height = bottom - top
    return pyautogui.screenshot(region=(left, top, width, height))

def enterWords(words, speed = 0.15):
    for word in words:
        # Move to the start of the word before selecting anything
        pyautogui.moveTo(word[0][0], word[0][1], speed)

        # Hold mouse down for the entire mouse moving sequence
        pyautogui.mouseDown()

        # Move over each letter
        for letter in word:
            pyautogui.moveTo(letter[0], letter[1], speed)
            pyautogui.mouseDown()

        # Release mouse up
        pyautogui.mouseUp()
        pyautogui.moveTo(500, 500, 0)
        time.sleep(1)

while True:
    v = Vision(SCREEN_COORDS)
    v.getBoardState()

while(True):
    # Get level image
    levelImage = screenshot(SCREEN_COORDS[0], SCREEN_COORDS[1], SCREEN_COORDS[2], SCREEN_COORDS[3])

    # Get level state, coords and word lengths required
    state, coords, wordLengths = WordbrainCv(TESSERACT_PATH).image_to_state(levelImage)

    # Generate solutions
    solutions = solveLevel([c.lower() for c in state], wordLengths)

    for solution in solutions:

        mouseCoords = [[GRID_COORDS[int(math.sqrt(len(state)))-2][i] for i in s] for s in solution]
        enterWords(mouseCoords)

        time.sleep(2)
        completeImage = screenshot(SCREEN_COORDS[0], SCREEN_COORDS[1], SCREEN_COORDS[2], SCREEN_COORDS[3])
        
        if GameCompleteCV().image_to_gameover(completeImage):
            time.sleep(3)
            break

        pyautogui.click(112, 612, clicks=3)
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        time.sleep(2)
