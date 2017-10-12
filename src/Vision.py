import numpy as np
from mss import mss
import time
import os
import cv2
import pytesseract
from multiprocessing import Pool
from PIL import Image

# Get a char from an image and add it to the output queue
def getCharFromImage(image):
    conf = '-psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return pytesseract.image_to_string(image, config=conf).lower()


class Vision:
    # topleft coord %, mid distance x %, mid distance y %, width x %, width y %
    GRID_CENTRES = (((0.270, 0.320), 0.490, 0.2900, 0.120, 0.080),  # 2x2
                    ((0.190, 0.265), 0.320, 0.1900, 0.080, 0.060),  # 3x3
                    ((0.141, 0.247), 0.248, 0.1440, 0.060, 0.040),  # 4x4
                    ((0.115, 0.234), 0.192, 0.1125, 0.045, 0.025),  # 5x5
                    ((0.093, 0.221), 0.160, 0.0941, 0.040, 0.024),  # 6x6
                    ((0.089, 0.215), 0.138, 0.0820, 0.035, 0.021),  # 7x7
                    ((0.082, 0.209), 0.122, 0.0710, 0.034, 0.020))  # 8x8
    RESET_BUTTON = (0.306, 0.950)   # Location of reset button
    AD_BUTTON = (0.960, 0.078)      # Location of close ad button

    def __init__(self, screenCoords, isRetina):
        self.isRetina = isRetina
        self.left = screenCoords[0]
        self.top = screenCoords[1]
        self.height = screenCoords[3] - screenCoords[1]
        self.width = screenCoords[2] - screenCoords[0]
        self.capture = mss()

    # Takes a screenshot of the specified region
    def getImage(self, left, top, width, height):
        if self.isRetina:
            left /= 2
            top /= 2
            width /= 2
            height /= 2

        return self.capture.grab({'left': left, 'top': top, 'width': width, 'height': height})

    # Gets board ratio of whiteness
    def getBoardRatio(self):
        # Compute board coordinates
        left = self.left
        top = self.top + int(0.2 * self.height)
        width = self.width
        height = int(0.7 * self.height) - int(0.2 * self.height)

        # Get screenshot of game board
        board = np.array(self.getImage(left, top, width, height))
        grayImage = cv2.cvtColor(board, cv2.COLOR_BGRA2GRAY)
        # Image.fromarray(grayImage).save('../resources/debug/board-' + str(time.time()) + '.png')

        # Get height and width
        h, w = grayImage.shape

        # Return total whiteness of the screen
        ratio = sum([1 if grayImage[y][x] >= 100 else 0 for x in range(0, w, w // 32) for y in range(0, h, h // 32)])
        return ratio

    # Gets cell ratio of whiteness
    def getCellRatio(self, i, numBoxes):
        # Compute cell coordinates
        x = i % numBoxes
        y = i // numBoxes
        grid = Vision.GRID_CENTRES[numBoxes - 2]
        topLeft = [grid[0][0] - grid[3], grid[0][1] - grid[4]]
        halfWidth = int(grid[3] * self.width)
        left = int((topLeft[0] + x * grid[1]) * self.width)
        top = int((topLeft[1] + y * grid[2]) * self.height) + halfWidth
        width = halfWidth * 2
        height = width

        # Get screenshot of cell
        cell = np.array(self.getImage(left, top, width, height))
        grayImage = cv2.cvtColor(cell, cv2.COLOR_BGRA2GRAY)
        # Image.fromarray(grayImage).save('../resources/debug/cell-' + str(time.time()) + '.png')

        # Get height and width
        h, w = grayImage.shape

        # Return total whiteness of the screen
        ratio = sum([1 if grayImage[y][x] >= 200 else 0 for x in range(0, w, w // 32) for y in range(0, h, h // 32)])
        return ratio

    # Scan first row in grid and return the number of boxes found
    def getNumBoxes(self, image):
        numBoxes = 0  # number of boxes in the row
        blackFlag = True  # flag of whether we're currently on black pixels
        startY = int(0.19 * self.height)  # height of the first row in the grid

        for x in range(image.shape[1]):
            pixel = image[startY][x]

            if pixel >= 200 and blackFlag:  # we found a white grid!
                numBoxes += 1
                blackFlag = False

            if pixel < 200 and not blackFlag:  # we found the end of the grid
                blackFlag = True

        return numBoxes

    # Get a list of chars from the image
    def getCharsFromImage(self, image):
        # Get number of boxes in the grid (along one side)
        numBoxes = self.getNumBoxes(image)

        # If out of range, return empty list of chars
        if numBoxes - 2 >= len(Vision.GRID_CENTRES):
            # print('Number of boxes is out of grid range:', numBoxes)
            return []

        # Get grid centres and calculate their char widths
        grid = Vision.GRID_CENTRES[numBoxes - 2]
        width = int(grid[3] * 2 * self.width)

        # Loop over each box in the grid and get its charImage
        charImages = []
        for j in range(numBoxes):
            for i in range(numBoxes):
                # Calculate top left coordinate for the current box
                topLeft = [grid[0][0] - grid[3], grid[0][1] - grid[4]]
                topLeft[0] = int((topLeft[0] + i * grid[1]) * self.width)
                topLeft[1] = int((topLeft[1] + j * grid[2]) * self.height)

                # Get image of char
                charImage = image[topLeft[1]:topLeft[1] + width, topLeft[0]:topLeft[0] + width]
                # Image.fromarray(charImage).save('../resources/debug/char-' + str(time.time()) + '.png')
                charImages.append(Image.fromarray(charImage))

        return Pool().map(getCharFromImage, charImages)

    def getWord(self, image, startX, startY):
        # Find starting X and letterbox sideLength
        sideLength = None
        for x in range(startX, image.shape[1]):
            pixel = image[startY][x][0]

            # If black pixel
            if pixel < 30:
                continue

            # White edge was found! Let's look for its right edge
            lowFlag = False
            for i in range(x, min(image.shape[1], x + int(0.1 * image.shape[1]))):
                pixel = image[startY][i][0]

                # If black pixel
                if pixel < 30 and not lowFlag:
                    lowFlag = True
                    continue

                # If low flag has been set, we've found a right edge!
                if pixel >= 30 and lowFlag:
                    sideLength = i - x
                    break
            break

        # Check we found a sideLength
        if sideLength is None:
            return

        # Find top edge
        for y in reversed(range(0, startY)):
            # Check if top edge was found
            if image[y][x + sideLength // 2][0] >= 30:
                break
        else:
            # Top edge was not found
            return

        # Count number of letters
        wordLength = 0
        x += sideLength // 2
        while x < image.shape[1]:
            # If black pixel, end of word
            if image[y][x][0] < 30:
                break

            # Otherwise, increment word
            wordLength += 1
            # print(wordLength, x, sideLength)

            # Find left edge of current letterbox
            for i in reversed(range(x - sideLength, x)):
                if image[startY][i][0] >= 30:
                    break

            # Jump into next char
            x = int(i + sideLength * (3 / 2))

        # Return word length and its final check position
        return wordLength, x, int(y + sideLength * (3 / 2))

    # Get a list of word lengths from the image
    def getWordLengthsFromImage(self, image, chars):
        top = int(0.74 * self.height)
        bottom = int(0.90 * self.height)
        croppedImage = image[top:bottom, :]

        startX = 0  # Should be a valid x position for start of row
        startY = 0  # Should be a valid y position for start of row
        heightJump = int(0.15 * croppedImage.shape[0])  # Should be a valid y jump

        # First level has "Words to find" text in the way, this catches it
        if len(chars) == 4:
            startY = int(0.25 * croppedImage.shape[0])

        words = []
        while startY < croppedImage.shape[0]:
            result = self.getWord(croppedImage, startX, startY)
            # print(result, startX, startY, heightJump)

            # If no words were found or we've read all we can from this row, go into next row
            if result is None or result[1] >= croppedImage.shape[1]:
                startY += heightJump
                startX = 0
                continue

            wordLength, endX, endY = result
            words.append(wordLength)
            heightJump = endY - startY
            startX = endX

        return words

    # Get board state from the current screen
    def getBoardState(self):
        # Get screenshot of game state
        screen = self.getImage(self.left, self.top, self.width, self.height)
        image = cv2.cvtColor(np.array(screen), cv2.COLOR_BGRA2RGB)
        # Image.fromarray(image).save('../resources/debug/screen-' + str(time.time()) + '.png')

        # Convert image to grayscale
        grayImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Image.fromarray(grayImage).save('../resources/debug/gray-' + str(time.time()) + '.png')

        # Get a list of chars from the board state
        chars = self.getCharsFromImage(grayImage)
        if chars == []:
            return [], []

        # Get a list of word lengths
        words = self.getWordLengthsFromImage(image, chars)

        # Return state
        return chars, words
