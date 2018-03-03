import multiprocessing as mp
import numpy as np
from mss import mss
import cv2
import pytesseract
from PIL import Image

# Get a char from an image and add it to the output queue
def get_char_from_image(image):
    conf = '-psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return pytesseract.image_to_string(image, config=conf).lower()


class Vision:
    # top_left coord %, mid distance x %, mid distance y %, width x %, width y %
    GRID_CENTRES = (((0.270, 0.320), 0.490, 0.2900, 0.120, 0.080),  # 2x2
                    ((0.190, 0.265), 0.320, 0.1900, 0.080, 0.060),  # 3x3
                    ((0.141, 0.247), 0.248, 0.1440, 0.060, 0.040),  # 4x4
                    ((0.115, 0.234), 0.192, 0.1125, 0.045, 0.025),  # 5x5
                    ((0.093, 0.221), 0.160, 0.0941, 0.040, 0.024),  # 6x6
                    ((0.089, 0.215), 0.138, 0.0820, 0.035, 0.021),  # 7x7
                    ((0.082, 0.209), 0.122, 0.0710, 0.034, 0.020))  # 8x8
    RESET_BUTTON = (0.306, 0.950)   # Location of reset button
    AD_BUTTON = (0.960, 0.078)      # Location of close ad button

    def __init__(self, screenCoords, is_retina):
        self.is_retina = is_retina
        self.left = screenCoords[0]
        self.top = screenCoords[1]
        self.height = screenCoords[3] - screenCoords[1]
        self.width = screenCoords[2] - screenCoords[0]
        self.capture = mss()

    # Takes a screenshot of the specified region
    def get_image(self, left, top, width, height):
        if self.is_retina:
            left /= 2
            top /= 2
            width /= 2
            height /= 2

        return self.capture.grab({'left': left, 'top': top, 'width': width, 'height': height})

    # Gets board image array
    def get_board(self):
        # Compute board coordinates
        left = self.left
        top = self.top + int(0.2 * self.height)
        width = self.width
        height = int(0.7 * self.height) - int(0.2 * self.height)

        # Get screenshot of game board
        board = np.array(self.get_image(left, top, width, height))
        gray_image = cv2.cvtColor(board, cv2.COLOR_BGRA2GRAY)
        # Image.fromarray(gray_image).save('../resources/debug/board-' + str(time.time()) + '.png')

        return gray_image

    # Gets board ratio of whiteness
    def get_board_ratio(self):
        gray_image = self.get_board()
        height, width = gray_image.shape
        # Return total whiteness of the screen
        ratio = sum([1 if gray_image[y][x] >= 100 else 0
                     for x in range(0, width, width // 32)
                     for y in range(0, height, height // 32)])
        return ratio

    # Gets cell image array
    def get_cell(self, i, num_boxes):
        # Compute cell coordinates
        col = i % num_boxes
        row = i // num_boxes
        grid = Vision.GRID_CENTRES[num_boxes - 2]
        top_left = [grid[0][0] - grid[3], grid[0][1] - grid[4]]
        half_width = int(grid[3] * self.width)
        left = int((top_left[0] + col * grid[1]) * self.width)
        top = int((top_left[1] + row * grid[2]) * self.height) + half_width
        width = half_width * 2
        height = width

        # Get screenshot of cell
        cell = np.array(self.get_image(left, top, width, height))
        gray_image = cv2.cvtColor(cell, cv2.COLOR_BGRA2GRAY)
        # Image.fromarray(gray_image).save('../resources/debug/cell-' + str(time.time()) + '.png')

        return gray_image

    # Gets cell ratio of whiteness
    def get_cell_ratio(self, i, num_boxes):
        gray_image = self.get_cell(i, num_boxes)
        height, width = gray_image.shape
        # Return total whiteness of the screen
        ratio = sum([1 if gray_image[y][x] >= 200 else 0
                     for x in range(0, width, width // 32)
                     for y in range(0, height, height // 32)])
        return ratio

    # Scan first row in grid and return the number of boxes found
    def get_num_boxes(self, image):
        num_boxes = 0  # number of boxes in the row
        black_flag = True  # flag of whether we're currently on black pixels
        start_y = int(0.19 * self.height)  # height of the first row in the grid
        for x_coord in range(image.shape[1]):
            pixel = image[start_y][x_coord]
            # Check if we've found a white box
            if pixel >= 200 and black_flag:
                num_boxes += 1
                black_flag = False
            # Check if we've found the end of a grid
            if pixel < 200 and not black_flag:
                black_flag = True
        return num_boxes

    # Get a list of chars from the image
    def get_chars_from_image(self, image):
        # Get number of boxes in the grid (along one side)
        num_boxes = self.get_num_boxes(image)

        # If out of range, return empty list of chars
        if num_boxes - 2 >= len(Vision.GRID_CENTRES):
            # print('Number of boxes is out of grid range:', num_boxes)
            return []

        # Get grid centres and calculate their char widths
        grid = Vision.GRID_CENTRES[num_boxes - 2]
        width = int(grid[3] * 2 * self.width)

        # Loop over each box in the grid and get its char_image
        char_images = []
        for j in range(num_boxes):
            for i in range(num_boxes):
                # Calculate top left coordinate for the current box
                top_left = [grid[0][0] - grid[3], grid[0][1] - grid[4]]
                top_left[0] = int((top_left[0] + i * grid[1]) * self.width)
                top_left[1] = int((top_left[1] + j * grid[2]) * self.height)

                # Get image of char
                char_image = image[top_left[1]:top_left[1] + width, top_left[0]:top_left[0] + width]
                # Image.fromarray(char_image).save('../resources/debug/char-' + str(time.time()) + '.png')
                char_images.append(Image.fromarray(char_image))

        return mp.Pool().map(get_char_from_image, char_images)

    def get_word(self, image, start_x, start_y):
        # Tracks the last position of the word we're entering
        last_x = -1
        # Find starting X and letterbox side_length
        side_length = None
        for x_coord in range(start_x, image.shape[1]):
            last_x = x_coord
            pixel = image[start_y][x_coord][0]
            # If black pixel, continue
            if pixel < 30:
                continue
            # White edge was found! Let's look for its right edge
            low_flag = False
            for i in range(x_coord, min(image.shape[1], x_coord + int(0.1 * image.shape[1]))):
                pixel = image[start_y][i][0]
                # If black pixel, set low flag and continue
                if pixel < 30 and not low_flag:
                    low_flag = True
                    continue
                # If low flag has been set, we've found a right edge!
                if pixel >= 30 and low_flag:
                    side_length = i - x_coord
                    break
            break

        # Check we found a side_length
        if side_length is None:
            return None

        # Find top edge
        for y_coord in reversed(range(0, start_y)):
            # Check if top edge was found
            if image[y_coord][last_x + side_length // 2][0] >= 30:
                top_edge = y_coord
                break
        else:
            # Top edge was not found
            return None

        # Count number of letters
        word_length = 0
        last_x += side_length // 2
        while last_x < image.shape[1]:
            # If black pixel, end of word
            if image[top_edge][last_x][0] < 30:
                break

            # Otherwise, increment word
            word_length += 1
            # print(word_length, last_x, side_length)

            # Find left edge of current letterbox
            for i in reversed(range(last_x - side_length, last_x)):
                if image[start_y][i][0] >= 30:
                    break

            # Jump into next char
            last_x = int(i + side_length * (3 / 2))

        # Return word length and its final check position
        return word_length, last_x, int(top_edge + side_length * (3 / 2))

    # Get a list of word lengths from the image
    def get_word_lengths_from_image(self, image, chars):
        top = int(0.74 * self.height)
        bottom = int(0.90 * self.height)
        cropped_image = image[top:bottom, :]

        start_x = 0  # Should be a valid x position for start of row
        start_y = 0  # Should be a valid y position for start of row
        height_jump = int(0.15 * cropped_image.shape[0])  # Should be a valid y jump

        # First level has "Words to find" text in the way, this catches it
        if len(chars) == 4:
            start_y = int(0.25 * cropped_image.shape[0])

        words = []
        while start_y < cropped_image.shape[0]:
            result = self.get_word(cropped_image, start_x, start_y)
            # print(result, start_x, start_y, height_jump)

            # If no words were found or we've read all we can from this row, go into next row
            if result is None or result[1] >= cropped_image.shape[1]:
                start_y += height_jump
                start_x = 0
                continue

            word_length, end_x, end_y = result
            words.append(word_length)
            height_jump = end_y - start_y
            start_x = end_x

        return words

    # Get board state from the current screen
    def get_board_state(self):
        # Get screenshot of game state
        screen = self.get_image(self.left, self.top, self.width, self.height)
        image = cv2.cvtColor(np.array(screen), cv2.COLOR_BGRA2RGB)
        # Image.fromarray(image).save('../resources/debug/screen-' + str(time.time()) + '.png')

        # Convert image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Image.fromarray(gray_image).save('../resources/debug/gray-' + str(time.time()) + '.png')

        # Get a list of chars from the board state
        chars = self.get_chars_from_image(gray_image)
        if chars == []:
            return [], []

        # Get a list of word lengths
        words = self.get_word_lengths_from_image(image, chars)

        # Return state
        return chars, words
