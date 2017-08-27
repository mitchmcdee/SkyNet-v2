import numpy as np
import pyautogui
import cv2
import pytesseract
from PIL import Image

class Vision:
    # topleft coord, mid distance x, mid distance y, width x, width y
    GRID_CENTRES = ((  ),
                    (  ),
                    (  ),
                    ((0.145,0.242),0.245,0.144,0.055,0.032))

    def __init__(self, screenCoords):
        self.topLeft = [screenCoords[0], screenCoords[1]]
        self.height = screenCoords[3] - screenCoords[1]
        self.width = screenCoords[2] - screenCoords[0]

    def getScreenImage(self):
        return pyautogui.screenshot(region=(*self.topLeft, self.width, self.height))

    def getNumBoxes(self, image):
        numBoxes = 0
        blackFlag = True
        startY = int(0.208 * self.height)

        x = 0
        while x < image.shape[1]:
            pixel = image[startY][x]
            x += 1

            if pixel > 100 and blackFlag:
                blackFlag = False
                numBoxes += 1

            if pixel < 100 and not blackFlag:
                blackFlag = True

        return numBoxes

    def getBoardState(self):
        # Get screenshot of game state
        image = self.getScreenImage()

        # Convert image to grayscale and black and white
        grayImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        # Get number of boxes in the grid (along one side)
        numBoxes = self.getNumBoxes(grayImage)

        # Get word lengths for the grid
        wordLengths = self.getWordLengths(grayImage)

        print(numBoxes, wordLengths)

        state = []
        for j in range(numBoxes):
            for i in range(numBoxes):
                grid = Vision.GRID_CENTRES[numBoxes - 1]
                topLeft = [grid[0][0] - grid[3], grid[0][1] - grid[4]]
                topLeft[0] = int((topLeft[0] + i * grid[1]) * self.width)
                topLeft[1] = int((topLeft[1] + j * grid[2]) * self.height)
                width = (int(grid[3] * 2 * self.width), int(grid[4] * 2 * self.height))
                char = grayImage[topLeft[1]:topLeft[1] + width[1], topLeft[0]:topLeft[0] + width[0]]
                state.append(pytesseract.image_to_string(Image.fromarray(char), config='-psm 10'))
                
        print(state)
        Image.fromarray(grayImage).show()

        while True:
            pass
