import curses
import os
from threading import Thread
import time
import math

class Screen:
    def __init__(self):
        # Clear solution and worker log files
        with open('solutions.log', 'w'), open('workers.log', 'w'):
            pass

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

        # Threads to handle window refresh
        self.updateThread = Thread(target=self.update)
        self.updateThread.daemon = True
        self.running = True
        self.updateThread.start()

    def update(self):
        while self.running:
            BORDER_PADDING = 1
            height, width = self.screen.getmaxyx()
            divider = width // 2 - BORDER_PADDING * 2
            curses.resizeterm(height, width)

            with open('solutions.log', 'r') as s, open('workers.log', 'r') as w:
                solutionWrapLines = 0
                workerWrapLines = 0

                # TODO(mitch): clean this code up its U-G-L-Y, boilerplate

                # Add tail lines to solution window
                for output in reversed(self.tail(s, height - BORDER_PADDING * 2)):
                    numLines = math.ceil(len(output) / divider)

                    for i in reversed(range(numLines)):
                        y = height - 2 - solutionWrapLines - (numLines - 1 - i)
                        if y < BORDER_PADDING:
                            break
                        line = output[i * divider : (i + 1) * divider]
                        self.solutionWindow.addstr(y, BORDER_PADDING, line)

                    solutionWrapLines += numLines

                # Add tail lines to worker window
                for output in reversed(self.tail(w, height - BORDER_PADDING * 2)):
                    numLines = math.ceil(len(output) / divider)

                    for i in reversed(range(numLines)):
                        y = height - BORDER_PADDING * 2 - workerWrapLines - (numLines - 1 - i)
                        if y < BORDER_PADDING:
                            break
                        line = output[i * divider : (i + 1) * divider]
                        self.workerWindow.addstr(y, BORDER_PADDING, line)

                    workerWrapLines += numLines

                # Refresh windows
                self.solutionWindow.border()
                self.workerWindow.border()
                self.solutionWindow.refresh()
                self.workerWindow.refresh()

    def exit(self):
        self.running = False
        self.updateThread.join()
        del self.solutionWindow
        del self.workerWindow
        curses.endwin()

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
