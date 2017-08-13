import pyautogui
import time
import sys
from searchTrie import solveLevel
from cv import WordbrainCv

TESSERACT_PATH = '/usr/local/Cellar/tesseract/3.05.01/bin/tesseract'
SCREEN_COORDS = [0, 46, 730, 1290] # Mitch's COORDS

# TESSERACT_PATH = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
# SCREEN_COORDS = [5, 81, 983, 1825] # Charlies COORDS

TEST_STATE = [['e','g','g','t','e','n','s','i','n'], [6,3]]
# TEST_STATE = [['d','o','o','r','r','a','p','o','a','o','b','u','l','v','c','f'], [8,4,4]]
# TEST_STATE = [['e','n','r','d','l','o','c','o','h','b','a','t','r','t','r','e'], [6,5,5]]
# TEST_STATE = [['s','i','o','s','h','t','m','r','k','c','r','o','a','a','t','t','h','n','e','a','b','a','p','p','f'], [5,3,3,8,6]]
# TEST_STATE = [['b','g','r','t','e','k','l','a','e','e','r','c','c','t','r','w','h','i','t','e','r','e','o','b','u','e','r','s','h','g','b','i','r','g','l','i'], [6,7,6,7,5,5]]

def screenshot(left, top, right, bottom):
    width = right - left
    height = bottom - top
    return pyautogui.screenshot(region=(left, top, width, height))

def enterWord(word, speed = 0.5):
    print(word)

    # Move to the start of the word before selecting anything
    pyautogui.moveTo(word[0][0], word[0][1], speed)

    # Hold mouse down for the entire mouse moving sequence
    pyautogui.mouseDown()

    # Move over each letter
    for letter in word:
        pyautogui.moveTo(letter[0], letter[1], speed)

    # Release mouse up
    pyautogui.mouseUp()

levelImage = screenshot(SCREEN_COORDS[0], SCREEN_COORDS[1], SCREEN_COORDS[2], SCREEN_COORDS[3])
cv = WordbrainCv(TESSERACT_PATH)
state, coords, wordLengths = cv.image_to_state(levelImage)
solutions = solveLevel([c.lower() for c in state], wordLengths)

for solution in solutions[:1]:
    mouseCoords = [[list(map(lambda x: x//3, coords[i])) for i in s] for s in solution]
    enterWord(sum(mouseCoords, []))