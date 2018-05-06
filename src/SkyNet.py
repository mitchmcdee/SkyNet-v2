from math import sqrt
import time
import logging
import pyautogui
import numpy as np
from solver import Solver
from vision import Vision
from screen import Screen
from random import randint, random
from PIL import Image

LOGGER = logging.getLogger(__name__)
HANDLER = logging.FileHandler('solutions.log')
FORMATTER = logging.Formatter('%(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)

pyautogui.FAILSAFE = True           # Allows exiting the program by moving mouse to top left of screen
IS_RETINA = True                    # Mitch has a macbook
SCREEN_COORDS = [0, 50, 720, 1280]  # Mitch's screen coords

class SkyNet:
    def __init__(self):
        self.vision = Vision(SCREEN_COORDS, IS_RETINA)
        # self.screen = Screen()

    def moveWithRandom(self, x, y, pause):
        pyautogui.moveTo(x, y, pause=pause)
        pyautogui.moveRel(randint(0, 5), randint(0, 5), pause=0)
        pyautogui.mouseDown(pause=0)

    # Waits until all animations on board have stopped
    def wait_for_animation(self):
        while True:
            board_before = self.vision.get_board_image()
            time.sleep(0.1)
            board_after = self.vision.get_board_image()
            if self.vision.images_equal(board_before, board_after):
                break

    # Enters the given word onto the board
    def enter_word(self, word, path, width):
        # Wait for animations to stop, necessary for computing board ratio
        self.wait_for_animation()

        # board before entering word
        board_before = self.vision.get_board_image()

        # Move over each letter
        for i, letter in enumerate(word):
            cell_before = self.vision.get_cell_image(path[i], width)
            cell_after = cell_before
            start_time = time.time()
            not_equal_count = 0
            while not_equal_count < 3:
                not_equal_count += not self.vision.images_equal(cell_after, cell_before)
                # Check if we got stuck
                if (time.time() - start_time) >= 3:
                    print('got stuck!')
                    return None
                self.moveWithRandom(*letter, pause=0)
                cell_after = self.vision.get_cell_image(path[i], width)
        pyautogui.mouseUp(pause=0.1)

        # Wait for animations to stop, necessary for computing board ratio
        self.wait_for_animation()

        # Return true if entered word was valid (board states were different), else false
        board_after = self.vision.get_board_image()
        return not self.vision.images_equal(board_before, board_after)

    # Click the button at the given relative width and height
    def click_button(self, width_percentage, height_percentage):
        width = width_percentage * self.vision.w
        height = height_percentage * self.vision.h
        # if on retina display, halve the mouse resolution due to scaling
        if IS_RETINA:
            width /= 2
            height /= 2
        pyautogui.moveTo(width, height, pause=0)
        pyautogui.mouseDown(pause=0.025)
        pyautogui.mouseUp(pause=0.025)

    # Resets the game board and exits any ads on screen
    def reset_board(self):
        while True:
            board_before = self.vision.get_board_image()
            self.click_button(*self.vision.AD_BUTTON)
            self.click_button(*self.vision.RESET_BUTTON)
            time.sleep(0.2)
            if not self.vision.images_equal(board_before, self.vision.get_board_image()):
                self.wait_for_animation()
                break

    # Generates a mouse grid for clicking board tiles
    def generate_mouse_grid(self, width):
        grid = self.vision.GRID_CENTRES[width - 2]
        mouse_grid = []
        for j in range(width):
            for i in range(width):
                col = int((grid[0][0] + i * grid[1]) * self.vision.w)
                row = int((grid[0][1] + j * grid[2]) * self.vision.h) + SCREEN_COORDS[1]
                # if on retina display, halve the mouse resolution due to scaling
                if IS_RETINA:
                    col /= 2
                    row /= 2
                mouse_grid.append((col, row))
        return mouse_grid

    def is_valid_state(self, chars, word_lengths):
        if chars is None or word_lengths is None:
            return False
        width = int(sqrt(len(chars)))
        return width is not None and width != 0 and width ** 2 == len(chars) \
               and len(chars) == sum(word_lengths) and len(chars) >= 4

    # Runs SkyNet
    def run(self):
        # Wait for screen to become responsive (anrdoid emulator? osx? idek lol)
        self.reset_board()
        # Play the game!
        while True:
            # # Clear screen
            # self.screen.clear()
            # Wait for any lingering animations
            self.wait_for_animation()

            # state = ['n', 'a', 'r', 'i', 'e', 't', 's', 'e', 'u', 'd', 't', 'r', 't', 'a', 'l', 't', 'e', 'a', 't', 'h', 'a', 'h', 'c', 'v', 'i', 'l', 'b', 'o', 'l', 'e', 'm', 's', 'g', 'f', 'p', 'l']
            # word_lengths = [7, 6, 7, 4, 4, 3, 5]

            # Get level state and word lengths required
            chars, word_lengths = self.vision.get_level_starting_state()
            print(chars, word_lengths)

            # Check valid state
            if not self.is_valid_state(chars, word_lengths):
                LOGGER.info('Invalid state, resetting')
                self.reset_board()
                continue

            width = int(sqrt(len(chars)))

            # Generate mouse grid
            mouse_grid = self.generate_mouse_grid(width)
            # Keep track of time taking to generate solutions
            start_time = time.time()
            # Loop over valid solutions to try them all
            with Solver() as solver:
                for solution in solver.get_solutions(chars, word_lengths):
                    # Compute time it took to find a solution
                    solution_time = str(round(time.time() - start_time, 2))
                    LOGGER.info(f'{solution_time}s - Testing: {solution.words}')
                    # Tracks the last position of the word we're entering
                    last_position = -1
                    # Get mouse coordinates for solution and enter them
                    for i, path in enumerate(solution.path):
                        last_position = i
                        word = ''.join([solution.all_states[i][j] for j in path])
                        LOGGER.info(f'entering {word}')
                        solver.add_tested_word(word)
                        was_bad_word = False
                        while True:
                            is_valid = self.enter_word([mouse_grid[i] for i in path], path, width)
                            # If the same ratio, the word entered was a bad one, so remove it from all solutions
                            if is_valid is False:
                                solver.add_bad_word(word)
                                LOGGER.info(f'added {word} as a bad word')
                                was_bad_word = True
                                break
                            elif is_valid is True:
                                break
                        if was_bad_word:
                            break
                    # Else if no break, all words in solution were entered, exit out of entering solutions
                    else:
                        if len(solution.words) == len(word_lengths):
                            break
                    # If we only entered one word incorrectly, we don't need to clear screen
                    if len(solution.path) > 0 and last_position == 0 and not is_valid:
                        continue
                    # Reset board for next solution
                    self.reset_board()

if __name__ == '__main__':
    SkyNet().run()
