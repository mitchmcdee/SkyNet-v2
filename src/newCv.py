import numpy as np
import pyautogui
import cv2
import pytesseract
from multiprocessing import Process, Queue
from PIL import Image

class Vision:
    # topleft coord %, mid distance x %, mid distance y %, width x %, width y %
    GRID_CENTRES = (((0.270,0.320),0.490,0.290,0.12,0.08),  # 2x2
                    ((0.190,0.265),0.320,0.190,0.08,0.06),  # 3x3
                    ((0.145,0.240),0.245,0.145,0.06,0.04))  # 4x4

    def __init__(self, screenCoords):
        self.topLeft = [screenCoords[0], screenCoords[1]]
        self.height = screenCoords[3] - screenCoords[1]
        self.width = screenCoords[2] - screenCoords[0]

    def getScreenImage(self):
        return pyautogui.screenshot(region=(*self.topLeft, self.width, self.height))

    # Scan first row in grid and return the number of boxes found
    def getNumBoxes(self, image):
        numBoxes = 0                            # number of boxes in the row
        blackFlag = True                        # flag of whether we're currently on black pixels
        startY = int(0.208 * self.height)       # height of the first row in the grid

        for x in range(0, image.shape[1]):
            pixel = image[startY][x]

            if pixel > 100 and blackFlag:       # we found a white grid!
                blackFlag = False
                numBoxes += 1

            if pixel < 100 and not blackFlag:   # we found the end of the grid
                blackFlag = True

        return numBoxes

    def getCharFromImage(self, index, image, outQueue):
        charText = pytesseract.image_to_string(image, config='-psm 10')
        outQueue.put((index, charText))

    def getCharsFromImage(self, image):
        # Get number of boxes in the grid (along one side)
        numBoxes = self.getNumBoxes(image)

        # Get grid centres and calculate their char widths
        grid = Vision.GRID_CENTRES[numBoxes - 2]
        width = (int(grid[3] * 2 * self.width), int(grid[4] * 2 * self.height))

        # Loop over each box in the grid and get its charImage
        state = []
        for j in range(numBoxes):
            for i in range(numBoxes):
                # Calculate top left coordinate for the current box
                topLeft = [grid[0][0] - grid[3], grid[0][1] - grid[4]]
                topLeft[0] = int((topLeft[0] + i * grid[1]) * self.width)
                topLeft[1] = int((topLeft[1] + j * grid[2]) * self.height)

                # Get image of char and save it to the state
                charImage = image[topLeft[1]:topLeft[1] + width[1], topLeft[0]:topLeft[0] + width[0]]
                state.append(Image.fromarray(charImage))

        # Loop over each char image and spawn a process to get its char form
        outQueue = Queue()
        processes = []
        for i in range(len(state)):
            p = Process(target=self.getCharFromImage, args=(i, state[i], outQueue))
            processes.append(p)
            p.start()

        # Wait for pytesseract processes to finish
        [p.join() for p in processes]

        # Collect and return all char results
        return sorted([outQueue.get() for _ in range(len(processes))], key=lambda x: x[0])

    def getWordLengthsFromImage(self, image):
        startY = int(0.804 * self.height)
        widthJump = int(0.076 * self.width)
        heightJump = int(0.05 * self.height)

        # TODO(mitch): everything works, just need to get width jump and height jump which varies puzzle to puzzle

        words = []
        topY = startY - heightJump
        for _ in range(3):
            # Find the first word's left edge
            x = 0
            while x < image.shape[1]:
                pixel = image[startY][x]

                # Check if we've found a white edge
                if pixel > 100:
                    # Add half the width of a word box
                    x += widthJump // 2
                    break

                x += 1

            # Check that x isn't at the right edge of the screen (aka failed to find a row)
            if x == image.shape[1]:
                break

            # Find the first word's top edge
            y = topY
            while y < image.shape[0]:
                pixel = image[y][x]

                # Check if we've found a white edge
                if pixel > 100:
                    break

                y += 1

            topY = y + int(0.047 * self.height)
            startY = topY + heightJump // 2

            wordLength = 0
            for i in range(x, image.shape[1], widthJump):
                pixel = max([image[y+j][i] for j in range(-10,10)])

                # Check if we've found a white edge
                if pixel > 100:
                    wordLength += 1
                    print(i, pixel, 'inc')
                elif wordLength != 0:
                    words.append(wordLength)
                    wordLength = 0
                    print(i, pixel, 'added')

        return words

    def getBoardState(self):
        # Get screenshot of game state
        image = self.getScreenImage()

        # Convert image to grayscale and black and white
        grayImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        Image.fromarray(grayImage).show() 

        # Get list of chars from the board state
        chars = self.getCharsFromImage(grayImage)
        # print(chars)

        words = self.getWordLengthsFromImage(grayImage)
        print(words)


        while True:
            pass
