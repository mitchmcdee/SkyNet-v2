import multiprocessing as mp
import numpy as np
from mss import mss
import cv2
import pytesseract
from PIL import Image
import time

def get_char_from_image(image):
    '''
    Returns the first char found within an image.
    '''
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
        self.x = screenCoords[0]
        self.y = screenCoords[1]
        self.w = screenCoords[2] - screenCoords[0]
        self.h = screenCoords[3] - screenCoords[1]
        self.capture = mss()

    def images_equal(self, image1, image2):
        picture1 = image1 / 255.0
        picture2 = image2 / 255.0
        picture1_norm = picture1/np.sqrt(np.sum(picture1**2))
        picture2_norm = picture2/np.sqrt(np.sum(picture2**2))
        return np.sum(picture2_norm*picture1_norm) >= 0.999

    def get_image(self, x, y, w, h):
        '''
        Returns a screen shot of the specified region.
        '''
        if self.is_retina:
            x /= 2
            y /= 2
            w /= 2
            h /= 2

        return self.capture.grab({'left': x, 'top': y, 'width': w, 'height': h})

    def get_board_image(self):
        '''
        Returns an array of the image representing the board.
        '''
        x, y, w, h = self.x, int(self.y + 0.17 * self.h), self.w, int(0.58 * self.h)
        board = np.array(self.get_image(x, y, w, h))
        gray_image = cv2.cvtColor(board, cv2.COLOR_BGRA2GRAY)
        # self.save_debug_image(gray_image, 'board')
        return gray_image

    def get_word_tiles_image(self):
        '''
        Returns an array of the image representing the word tiles.
        '''
        x, y, w, h = self.x, int(self.y + 0.75 * self.h), self.w, int(0.15 * self.h)
        board = np.array(self.get_image(x, y, w, h))
        gray_image = cv2.cvtColor(board, cv2.COLOR_BGRA2GRAY)
        # self.save_debug_image(gray_image, 'word_tiles')
        return gray_image

    # Gets cell image array
    def get_cell_image(self, i, num_boxes):
        # Compute cell coordinates
        col = i % num_boxes
        row = i // num_boxes
        grid = Vision.GRID_CENTRES[num_boxes - 2]
        top_x = [grid[0][0] - grid[3], grid[0][1] - grid[4]]
        half_w = int(grid[3] * self.w)
        x = int((top_x[0] + col * grid[1]) * self.w)
        y = int((top_x[1] + row * grid[2]) * self.h) + half_w
        w = half_w * 2
        h = w

        # Get screenshot of cell
        cell = np.array(self.get_image(x, y, w, h))
        gray_image = cv2.cvtColor(cell, cv2.COLOR_BGRA2GRAY)
        # self.save_debug_image(gray_image, 'cell')

        return gray_image

    def save_debug_image(self, image_array, prefix):
        file_path = f'../resources/debug/{prefix}-{time.time()}.png'
        Image.fromarray(image_array).save(file_path)

    def get_cropped_box(self, image):
        _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        # Morph-op to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        # Find the max-area contour
        _, contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return None
        max_countour = sorted(contours, key=cv2.contourArea)[-1]
        bounding_box = cv2.boundingRect(max_countour)
        return bounding_box

    def get_padded_char_box(self, box):
        x, y, w, h = box
        padding = 3
        l = r = (max(w, h) - w) // 2 + padding
        t = b = (max(w, h) - h) // 2 + padding
        padded_box = x - l, y - t, w + l + r, h + t + b
        return padded_box

    def get_cropped_image(self, image, box):
        x, y, w, h = box
        cropped_image = image[y:y + h, x: x + w]
        return cropped_image

    def get_char_image(self, image, box):
        full_char_image = self.get_cropped_image(image, box)
        cropped_box = self.get_cropped_box(full_char_image)
        if cropped_box is None:
            return None
        padded_box = self.get_padded_char_box(cropped_box)
        cropped_char_image = self.get_cropped_image(full_char_image, padded_box)
        char_image = Image.fromarray(cropped_char_image)
        return char_image

    def get_grid_boxes(self, image, threshold_val, hierarchy_index):
        _, thresh = cv2.threshold(image, threshold_val, 255, cv2.THRESH_BINARY)
        self.save_debug_image(thresh, 'idk')
        _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
        contours = [c for i, c in enumerate(contours)
                    if hierarchy[0, i, hierarchy_index] == -1]
        boxes = [cv2.boundingRect(c) for c in contours]
        boxes = [(x, y, w, h) for x, y, w, h in boxes
                 if abs(w - h) <= min(w, h) // 2]
        boxes.sort(key=lambda box: (box[1], box[0]))
        return boxes

    def get_board_chars(self):
        board_image = self.get_board_image()
        board_grid_boxes = self.get_grid_boxes(board_image, 127, 3)
        char_images = [self.get_char_image(board_image, box)
                       for box in board_grid_boxes]
        if any(image is None for image in char_images):
            return None
        chars = mp.Pool().map(get_char_from_image, char_images)
        return chars

    def get_board_word_lengths(self):
        word_tiles_image = self.get_word_tiles_image()
        word_tiles_grid_boxes = self.get_grid_boxes(word_tiles_image, 50, 2)
        prev_x = prev_y = delta_x = delta_y = None
        words = []
        word_length = 0
        for i, (x, y, w, h) in enumerate(word_tiles_grid_boxes):
            if i != 0 and (x >= prev_x + delta_x or y >= prev_y + delta_y):
                words.append(word_length)
                word_length = 0
            word_length += 1
            prev_x, prev_y, delta_x, delta_y = x, y, max(w, h) * 1.5, max(w, h) * 0.1
        return words + [word_length]

    # Get level's starting state from the current screen
    def get_level_starting_state(self):
        return self.get_board_chars(), self.get_board_word_lengths()
