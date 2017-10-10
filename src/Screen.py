import curses
import os
from threading import Thread

class Screen:
    def __init__(self):
        # Create screen
        self.screen = curses.initscr()
        self.screen.clear()
        curses.noecho()

        # Define 2 windows
        height, width = self.screen.getmaxyx()
        divider = width // 2
        self.solutionWindow = curses.newwin(height, divider, 0, 0)
        self.workerWindow = curses.newwin(height, divider, 0, divider)
        self.solutionWindow.border()
        self.workerWindow.border()

        # tThreads to handle window refresh
        thread = Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()
        thread.join()

    def update(self):
        while True:
            height, width = self.screen.getmaxyx()
            divider = width // 2

            with open('solutions.log', 'r') as s, open('workers.log', 'r') as w:
                # Add tail lines to solution window
                for i, line in enumerate(self.tail(s, 2)):
                    self.solutionWindow.addstr(i + 1, 1, line)

                # Add tail lines to worker window
                for i, line in enumerate(self.tail(w, 2)):
                    self.workerWindow.addstr(i + 1, 1, line)

                # Refresh windows
                self.solutionWindow.border()
                self.workerWindow.border()
                self.solutionWindow.refresh()
                self.workerWindow.refresh()

    # Author: glenbot
    # Source: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    def tail(self, f, lines=1, _buffer=4098):
        """Tail a file and get X lines from the end"""
        # place holder for the lines found
        lines_found = []    

        # block counter will be multiplied by buffer
        # to get the block size from the end
        block_counter = -1

        # loop until we find X lines
        while len(lines_found) < lines:
            try:
                f.seek(block_counter * _buffer, os.SEEK_END)
            except IOError:  # either file is too small, or too many lines requested
                f.seek(0)
                lines_found = f.readlines()
                break   

            lines_found = f.readlines() 

            # we found enough lines, get out
            # Removed this line because it was redundant the while will catch
            # it, I left it for history
            # if len(lines_found) > lines:
            #    break  

            # decrement the block counter to get the
            # next X bytes
            block_counter -= 1  

        return lines_found[-lines:]
