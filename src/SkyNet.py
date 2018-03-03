from math import sqrt
import time
import logging
import pyautogui
import numpy as np
from solver import Solver
from vision import Vision
from screen import Screen

LOGGER = logging.getLogger(__name__)
HANDLER = logging.FileHandler('solutions.log')
FORMATTER = logging.Formatter('%(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)

pyautogui.FAILSAFE = True           # Allows exiting the program by moving mouse to top left of screen
IS_RETINA = True                    # Mitch has a macbook
SCREEN_COORDS = [0, 46, 730, 1290]  # Mitch's screen coords

class SkyNet:
    def __init__(self):
        self.vision = Vision(SCREEN_COORDS, IS_RETINA)
        self.screen = Screen()

    # Waits until all animations on board have stopped
    def wait_for_animation(self):
        while True:
            board_before = self.vision.get_board()
            time.sleep(0.1)
            board_after = self.vision.get_board()
            if np.array_equal(board_before, board_after):
                break

    # Enters the given word onto the board
    def enter_word(self, word, path, width):
        # Wait for animations to stop, necessary for computing board ratio
        self.wait_for_animation()

        # board ratio before entering word
        start = self.vision.get_board_ratio()

        # Move over each letter
        for i, letter in enumerate(word):
            cell_before = self.vision.get_cell(path[i], width)
            cell_after = cell_before
            while np.array_equal(cell_after, cell_before):
                pyautogui.moveTo(*letter, pause=0)
                pyautogui.mouseDown(pause=0)
                cell_after = self.vision.get_cell(path[i], width)
        pyautogui.mouseUp(pause=0)

        # Wait for animations to stop, necessary for computing board ratio
        self.wait_for_animation()

        # Return true if entered word was valid (board states were different), else false
        return start != self.vision.get_board_ratio()

    # Click the button at the given relative width and height
    def click_button(self, width_percentage, height_percentage):
        width = width_percentage * self.vision.width
        height = height_percentage * self.vision.height
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
            board_before = self.vision.get_board_ratio()
            self.click_button(*self.vision.AD_BUTTON)
            self.click_button(*self.vision.RESET_BUTTON)
            self.click_button(SCREEN_COORDS[0] / self.vision.width, SCREEN_COORDS[1] / self.vision.height)
            time.sleep(0.3)
            if board_before != self.vision.get_board_ratio():
                self.wait_for_animation()
                break

    # Generates a mouse grid for clicking board tiles
    def generate_mouse_grid(self, width):
        grid = self.vision.GRID_CENTRES[width - 2]
        mouse_grid = []
        for j in range(width):
            for i in range(width):
                col = int((grid[0][0] + i * grid[1]) * self.vision.width)
                row = int((grid[0][1] + j * grid[2]) * self.vision.height) + SCREEN_COORDS[1]
                # if on retina display, halve the mouse resolution due to scaling
                if IS_RETINA:
                    col /= 2
                    row /= 2
                mouse_grid.append((col, row))
        return mouse_grid

    # Runs SkyNet
    def run(self):
        # Wait for screen to become responsive (anrdoid emulator? osx? idek lol)
        self.reset_board()
        # Play the game!
        while True:
            # Clear screen
            self.screen.clear()
            # Wait for any lingering animations
            self.wait_for_animation()

            # state = ['n', 'a', 'r', 'i', 'e', 't', 's', 'e', 'u', 'd', 't', 'r', 't', 'a', 'l', 't', 'e', 'a', 't', 'h', 'a', 'h', 'c', 'v', 'i', 'l', 'b', 'o', 'l', 'e', 'm', 's', 'g', 'f', 'p', 'l']
            # word_lengths = [7, 6, 7, 4, 4, 3, 5]

            # Get level state and word lengths required
            state, word_lengths = self.vision.get_board_state()
            width = int(sqrt(len(state)))
            LOGGER.info(f'{state} {word_lengths}')

            # Check state is reasonable
            if width == 0 or width ** 2 != len(state) or len(state) != sum(word_lengths) or len(state) < 4:
                LOGGER.info('Invalid state, resetting')
                self.reset_board()
                continue

            # Generate mouse grid
            mouse_grid = self.generate_mouse_grid(width)
            # Keep track of time taking to generate solutions
            start_time = time.time()
            # Loop over valid solutions to try them all
            with Solver() as solver:
                for solution in solver.get_solutions(state, word_lengths):
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
                        # If the same ratio, the word entered was a bad one, so remove it from all solutions
                        is_valid = self.enter_word([mouse_grid[i] for i in path], path, width)
                        if not is_valid:
                            solver.add_bad_word(word)
                            LOGGER.info(f'added {word} as a bad word')
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
