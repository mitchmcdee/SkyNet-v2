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

        self.processes = []
        manager = Manager()  # TODO(mitch): profile this and see if its performant
        self.badWords = manager.dict()  # Set of words not to search
        self.seenWords = manager.dict()  # Set of words already seen
        self.initialState = initialState  # Initial state of board
        self.wordLengths = wordLengths  # List of word lengths to look for

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
        [p.terminate() and p.join() for p in self.processes]

    # Add a bad word to avoid it being searched again
    def addBadWord(self, word):
        self.badWords[word] = 1

    # Worker which solves states and sends complete solutions to SolutionQueue
    def SolvingWorker(self, i, stack, solutionQueue):
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
                                solutions.append(solutionQueue.get_nowait())
                        except:
                            pass
                        solutionQueue.put(childState)
                        [solutionQueue.put(s) for s in solutions]
                        continue

                        # TODO (mitch): clean up everything in this file and comment

                    elif len(childState.state) >= 25 and childWord not in self.seenWords:
                        solutionQueue.put(childState)
                        self.seenWords[childWord] = 1

                    logger.info(f'{i}: {childState.words}')
                    stack.append(childState)

        # Send death message
        solutionQueue.put(i)

    # Solve the current level
    def getSolutions(self):
        logger.info('Getting solutions')
        solutionQueue = Queue()
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
                    solutionQueue.put(childState)
                    continue

                elif len(childState.state) >= 25 and childWord not in self.seenWords:
                    solutionQueue.put(childState)
                    self.seenWords[childWord] = 1

                logger.info(f'pre: {childState.words}')
                rootStates.append(childState)

        # Split root states up evenly to distribute to processes
        splitStates = [rootStates[i::numProcesses] for i in range(numProcesses)]

        # Create Solving Workers and delegate them work
        for i in range(numProcesses):
            p = Process(target=self.SolvingWorker, args=(i, splitStates[i], solutionQueue))
            self.processes.append(p)
            p.daemon = True
            p.start()

        # Keep looping while there are workers alive
        activeWorkers = len(self.processes)
        while True:
            # If there are no workers alive, we're done!
            if activeWorkers == 0:
                break

            solution = solutionQueue.get(1)

            # If there's no solution, continue
            if solution is None:
                continue

            # Check if was a death message
            if type(solution) == int:
                p = self.processes[solution]
                p.terminate() and p.join()
                activeWorkers -= 1
                logger.info(f'{solution} is finished! {activeWorkers} workers remaining')
                continue

            # Check solution doesn't contain any bad words
            if any(w in self.badWords for w in solution.words):
                continue

            yield solution
