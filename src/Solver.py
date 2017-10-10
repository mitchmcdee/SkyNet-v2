import sys
import os
from math import ceil
from multiprocessing import Pool, Queue, Process, Manager
from Trie import Trie, TrieNode
from State import State, StateNode
from collections import Counter
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('workers.log')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Solver:
    def __init__(self, initialState, wordLengths):
        # Clear worker log file
        with open('workers.log', 'w'):
            pass

        self.processes = {}
        manager = Manager()  # TODO(mitch): profile this and see if its performant
        self.badWords = manager.dict()  # Set of words not to search
        self.seenWords = manager.dict()  # Set of words already seen
        self.initialState = initialState  # Initial state of board
        self.wordLengths = wordLengths  # List of word lengths to look for
        self.solutionQueue = Queue()

        # Generate Trie
        self.trie = Trie()
        numWords = 0
        with open('../resources/goodWords.txt', 'r') as f:
            for line in f:
                word = line.strip('\n')

                if len(word) not in self.wordLengths:
                    continue

                stateCounter = Counter(initialState)
                wordCounter = Counter(word)
                stateCounter.subtract(wordCounter)

                if any(v < 0 for v in stateCounter.values()):
                    continue

                numWords += self.trie.addWord(word)
        logger.info(f'Added {numWords} words to trie')

    # Return self on enter
    def __enter__(self):
        return self

    # Tear down processes on exit
    def __exit__(self, t, v, traceback):
        [p.terminate() and p.join() for p in self.processes.values()]

    # Add a bad word to avoid it being searched again
    def addBadWord(self, word):
        self.badWords[word] = 1

    # Worker which solves states and sends complete solutions to SolutionQueue
    def SolvingWorker(self, i, initialState):
        logger.info(f'{i} is starting!')
        stack = [initialState]
        while len(stack) != 0:
            state = stack.pop()

            for root in state.getValidRoots(self.trie):
                for path in root.getValidPaths(self.trie, state):
                    childState = state.getRemovedPathState(path)
                    childWord = state.getWord(path)

                    # Check solution doesn't contain any bad words
                    if any(w in self.badWords for w in childState.words):
                        continue

                    # If there are no more words, we've found a complete solution
                    if len(childState.wordLengths) == 0:
                        solutions = []
                        try:
                            while True:
                                solutions.append(self.solutionQueue.get_nowait())
                        except:
                            pass
                        self.solutionQueue.put(childState)
                        [self.solutionQueue.put(s) for s in solutions]
                        continue

                        # TODO (mitch): clean up everything in this file and comment

                    elif len(childState.state) > 25 and childWord not in self.seenWords:
                        self.solutionQueue.put(childState)
                        self.seenWords[childWord] = 1

                    # logger.info(f'{i}: {childState.words}')
                    stack.append(childState)

        # Send death message
        self.solutionQueue.put(i)

    def startProcess(self, i, initialState):
        p = Process(target=self.SolvingWorker, args=(i, initialState))
        self.processes[i] = p
        p.daemon = True
        p.start()

    # Solve the current level
    def getSolutions(self):
        logger.info('Getting solutions')
        numProcesses = max(1, os.cpu_count() - 1)  # Ensure stability
        initialState = State(self.initialState, self.wordLengths)

        # Generate all root states
        rootStates = []
        for root in initialState.getValidRoots(self.trie):
            for path in root.getValidPaths(self.trie, initialState):
                childState = initialState.getRemovedPathState(path)
                childWord = initialState.getWord(path)

                # If there are no more words, we've found a complete solution
                if len(childState.wordLengths) == 0:
                    self.solutionQueue.put(childState)
                    continue

                elif len(childState.state) > 25 and childWord not in self.seenWords:
                    self.solutionQueue.put(childState)
                    self.seenWords[childWord] = 1

                # logger.info(f'pre: {childState.words}')
                rootStates.append(childState)

        # TODO(mitch): this solution for delegating work to workers properly
        # doesn't actually work. Only like 10% of the root states are actually
        # valid words, so you'll quickly reduce down to the same 3 active workers
        # you had originally anyway.
        #
        # you need to have some way of stealing stack elements from other processes.

        # Create Solving Workers and delegate them work
        for i in range(min(numProcesses, len(rootStates))):
            self.startProcess(i, rootStates.pop())

        # Keep looping while there are workers alive
        activeWorkers = len(self.processes)
        latestWorker = activeWorkers - 1
        remainingTasks = len(rootStates)
        while True:
            # If there are no workers alive, we're done!
            if activeWorkers == 0:
                break

            solution = self.solutionQueue.get(1)

            # If there's no solution, continue
            if solution is None:
                continue

            # Check if was a death message
            if type(solution) == int:
                logger.info(f'{solution} is finished!')
                p = self.processes[solution]
                p.terminate() and p.join()
                activeWorkers -= 1

                if remainingTasks > 0:
                    latestWorker += 1
                    self.startProcess(latestWorker, rootStates.pop())
                    remainingTasks -= 1
                    activeWorkers += 1

                continue

            # Check solution doesn't contain any bad words
            if any(w in self.badWords for w in solution.words):
                continue

            yield solution
