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
                    ((0.141,0.247),0.248,0.144,0.06,0.04))  # 4x4
    RESET_BUTTON =  (0.306,0.950)                           # Location of reset button
    AD_BUTTON =     (0.960,0.078)                           # Location of close ad button

    def __init__(self, screenCoords):
        self.topLeft = [screenCoords[0], screenCoords[1]]
        self.height = screenCoords[3] - screenCoords[1]
        self.width = screenCoords[2] - screenCoords[0]

    # Takes a screenshot of the screen region
    def getScreenImage(self):
        return pyautogui.screenshot(region=(*self.topLeft, self.width, self.height))

    # Checks if the entered solution was correct and we're at the level complete scene
    def checkLevelComplete(self):
        return self.getScreenRatio() < 0.8

    # Gets screen ratio of whiteness
    def getScreenRatio(self):
        # Get screenshot of game state
        image = self.getScreenImage()

        # Convert image to grayscale
        grayImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        # Get height and width
        height, width = grayImage.shape

        # Get threshold ratio of the game screen and compare it to the expected
        _, threshold = cv2.threshold(grayImage, 190, 255, cv2.THRESH_BINARY)
        return cv2.countNonZero(threshold) / float((height * width))

    # Gets board ratio of whiteness
    def getBoardRatio(self):
        # Get screenshot of game state
        image = self.getScreenImage()

        # Convert image to grayscale and crop it
        grayImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        croppedImage = grayImage[int(0.170 * self.height) : int(0.750 * self.height),:]

        # Get height and width
        height, width = croppedImage.shape

        # Get threshold ratio of the game screen and compare it to the expected
        _, threshold = cv2.threshold(croppedImage, 190, 255, cv2.THRESH_BINARY)
        return cv2.countNonZero(threshold) / float((height * width))

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

    # Get a char from an image and add it to the output queue
    def getCharFromImage(self, index, image, outQueue):
        charText = pytesseract.image_to_string(image, config='-psm 10')
        outQueue.put((index, charText if charText != '.' else 'P'))

    # Get a list of chars from the image
    def getCharsFromImage(self, image):
        # Get number of boxes in the grid (along one side)
        numBoxes = self.getNumBoxes(image)

        # If out of range, return empty list of chars
        if numBoxes - 2 >= len(Vision.GRID_CENTRES):
            return []

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
        return [c[1] for c in sorted([outQueue.get() for _ in range(len(processes))], key=lambda x: x[0])]

    # Get a list of word lengths from the image
    def getWordLengthsFromImage(self, image):
        # Loop over all possible rows (3)
        words = []
        startY = int(0.804 * self.height)       # Should be a valid y position of first row
        topY = startY - int(0.05 * self.height) # Should be a valid y position above first row
        widthJump = int(0.1 * self.width)       # Should be a valid width jump for now
        heightJump = int(0.07 * self.height) # Should be a valid height jump for now
        for _ in range(2):                      # TODO(mitch): make this work for 3
            # Find the first word's left edge
            x = 0
            while x < image.shape[1]:
                pixel = image[startY][x]

                # Check if we've found the left edge
                if pixel > 100:

                    # Find the width of a letter box
                    lowFlag = False
                    for i in range(x, x + widthJump):
                        pixel = image[startY][i]

                        # If we've hit a low pixel then see high again, we have hit another edge and know the width
                        if pixel < 100 and not lowFlag:
                            lowFlag = True
                        elif pixel > 100 and lowFlag:
                            widthJump = i - x + 3 # Offset to account for width of cell
                            break

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

                    # Find the height of a letter box
                    lowFlag = False
                    for i in range(y, y + heightJump):
                        pixel = image[i][x]

                        # If we've hit a low pixel then see high again, we have hit another edge and know the height
                        if pixel < 100 and not lowFlag:
                            lowFlag = True
                        elif pixel > 100 and lowFlag:
                            heightJump = i - y + 3 # Offset to account for height of cell
                            break

                    break

                y += 1

            # Calculate the topY and startY for the next row
            topY = y + heightJump
            startY = topY + heightJump // 2

            # Loop over potential letter locations to build words
            wordLength = 0
            for i in range(x, image.shape[1], widthJump):
                pixel = max([image[y+j][i] for j in range(10)])

                # Check if we've found a white edge
                if pixel > 100:
                    wordLength += 1

                # If we didn't find one, check the word we're adding is of valid length
                elif wordLength >= 2:
                    words.append(wordLength)
                    wordLength = 0

        return words

    # Get board state from the current screen
    def getBoardState(self):
        # Get screenshot of game state
        image = self.getScreenImage()

        # Convert image to grayscale
        grayImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        # Image.fromarray(grayImage).show()

        # Get a list of chars from the board state
        chars = self.getCharsFromImage(grayImage)

        # Get a list of word lengths
        words = self.getWordLengthsFromImage(grayImage)

        # Return state
        return chars, words
