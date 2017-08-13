import pyautogui
import time
import sys
from searchTrie import solveLevel
from cv import WordbrainCv
from cv_check import GameCompleteCV

pyautogui.FAILSAFE = True

TESSERACT_PATH = '/usr/local/Cellar/tesseract/3.05.01/bin/tesseract'
SCREEN_COORDS = [0, 46, 730, 1290] # Mitch's COORDS

# for 2x2, 3x3
GRID_COORDS = [[[94,218], [270,219], [94,393], [267,394]],
               [[65,193], [182,190], [299,190], [65,308], [182,309], [298,308], [67,421], [184,424], [299,425]]]

# TEST_STATE = [['e','g','g','t','e','n','s','i','n'], [6,3]]
# TEST_STATE = [['d','o','o','r','r','a','p','o','a','o','b','u','l','v','c','f'], [8,4,4]]
# TEST_STATE = [['e','n','r','d','l','o','c','o','h','b','a','t','r','t','r','e'], [6,5,5]]
# TEST_STATE = [['s','i','o','s','h','t','m','r','k','c','r','o','a','a','t','t','h','n','e','a','b','a','p','p','f'], [5,3,3,8,6]]
# TEST_STATE = [['b','g','r','t','e','k','l','a','e','e','r','c','c','t','r','w','h','i','t','e','r','e','o','b','u','e','r','s','h','g','b','i','r','g','l','i'], [6,7,6,7,5,5]]

def screenshot(left, top, right, bottom):
    width = right - left
    height = bottom - top
    return pyautogui.screenshot(region=(left, top, width, height))

def enterWords(words, speed = 0.2):
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


for i in range(20):
    # Get level image
    levelImage = screenshot(SCREEN_COORDS[0], SCREEN_COORDS[1], SCREEN_COORDS[2], SCREEN_COORDS[3])
    print("took screenie")

    # Get level state, coords and word lengths required
    state, coords, wordLengths = WordbrainCv(TESSERACT_PATH).image_to_state(levelImage)
    print(state)

    # Generate solutions
    solutions = solveLevel([c.lower() for c in state], wordLengths)

    for solution in solutions:
        mouseCoords = [[GRID_COORDS[1][i] for i in s] for s in solution]
        enterWords(mouseCoords)

        time.sleep(2)
        completeImage = screenshot(SCREEN_COORDS[0], SCREEN_COORDS[1], SCREEN_COORDS[2], SCREEN_COORDS[3])
        
        if GameCompleteCV().image_to_gameover(completeImage):
            time.sleep(1)
            break