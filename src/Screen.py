import curses
import os
from threading import Thread
import math

# Author: glenbot
# Source: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
def tail(file, lines=1, _buffer=4098):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            file.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            file.seek(0)
            lines_found = file.readlines()
            break

        lines_found = file.readlines()

        # we found enough lines, get out
        # Removed this line because it was redundant the while will catch
        # it, I left it for history
        # if len(lines_found) > lines:
        #    break

        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1

    return lines_found[-lines:]

# TODO(mitch): fix this API to reflect writing to screen instead of calling update
class Screen:
    # Number of characters to pad borders by
    BORDER_PADDING = 1

    def __init__(self):
        # Create screen
        self.screen = curses.initscr()
        self.screen.clear()
        curses.noecho()

        # Define 2 windows
        height, width = self.screen.getmaxyx()
        divider = width // 2
        self.solution_window = curses.newwin(height, divider, 0, 0)
        self.worker_window = curses.newwin(height, divider, 0, divider)
        self.solution_window.border()
        self.worker_window.border()

        # Threads to handle window refresh
        self.update_thread = Thread(target=self.update)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Clear log files
        self.clear()

        #TODO(mitch): add resizing!

    def update(self):
        while True:
            height, width = self.screen.getmaxyx()
            divider = width // 2 - self.BORDER_PADDING * 2
            curses.resizeterm(height, width)

            with open('solutions.log', 'r') as solutions, open('workers.log', 'r') as workers:
                solution_wrap_lines = 0
                worker_wrap_lines = 0

                # TODO(mitch): clean this code up its U-G-L-Y, boilerplate

                # Add tail lines to solution window
                for output in reversed(tail(solutions, height - self.BORDER_PADDING * 2)):
                    num_lines = math.ceil(len(output) / divider)

                    for i in reversed(range(num_lines)):
                        row = height - 2 - solution_wrap_lines - (num_lines - 1 - i)
                        if row < self.BORDER_PADDING:
                            break
                        line = output[i * divider : (i + 1) * divider]
                        self.solution_window.addstr(row, self.BORDER_PADDING, line)

                    solution_wrap_lines += num_lines

                # Add tail lines to worker window
                for output in reversed(tail(workers, height - self.BORDER_PADDING * 2)):
                    num_lines = math.ceil(len(output) / divider)

                    for i in reversed(range(num_lines)):
                        row = height - self.BORDER_PADDING * 2 - worker_wrap_lines - (num_lines - 1 - i)
                        if row < self.BORDER_PADDING:
                            break
                        line = output[i * divider : (i + 1) * divider]
                        self.worker_window.addstr(row, self.BORDER_PADDING, line)

                    worker_wrap_lines += num_lines

                # Refresh windows
                self.solution_window.border()
                self.worker_window.border()
                self.solution_window.refresh()
                self.worker_window.refresh()

    def clear(self):
        # Clear solution and worker log files
        with open('solutions.log', 'w'), open('workers.log', 'w'):
            pass

        self.solution_window.clear()
        self.worker_window.clear()
