import sys
import os
from math import ceil
from multiprocessing import Pool, Queue, Process
from Trie import Trie, TrieNode
from State import State, StateNode
from collections import Counter

class Solver:
    def __init__(self, initialState, wordLengths, badWords = []):
        self.processes = []
        self.badWords = set()               # Set of words not to search
        self.initialState = initialState    # Initial state of board
        self.wordLengths = wordLengths      # List of word lengths to look for

        # Generate Trie
        self.trie = Trie()
        numWords = 0
        # with open('../resources/bigWords.txt', 'r') as f:
        with open('../resources/goodWords.txt', 'r') as f:
        # with open('../resources/norvigWordsAll.txt', 'r') as f:
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
        print('Added ' + str(numWords) + ' words to trie')

    # Return self on enter
    def __enter__(self):
        return self

    # Tear down processes on exit
    def __exit__(self, type, value, traceback):
        [p.terminate() and p.join() for p in self.processes]

    # Add a bad word to avoid it being searched again
    def addBadWord(self, word):
        self.badWords.add(word.lower())

    # Worker which solves states and sends complete solutions to SolutionQueue
    def SolvingWorker(self, i, stack, solutionQueue):
        while len(stack) != 0:
            state = stack.pop()

            for root in state.getValidRoots(self.trie):
                for path in root.getValidPaths(self.trie, state):
                    childState = state.getRemovedPathState(path)

                    # Check solution doesn't contain any bad words
                    if not childState.words.isdisjoint(self.badWords):
                        continue

                    # If there are no more words, we've found a complete solution
                    if len(childState.wordLengths) == 0:
                        solutionQueue.put(childState)
                        continue

                    # print(i, childState.words)
                    stack.append(childState)

        # Send death message
        print(i, 'is finished, exiting!')
        solutionQueue.put(i)

    # Solve the current level
    def getSolutions(self):
        solutionQueue = Queue()
        numProcesses = max(1, os.cpu_count() - 1) # Ensure stability
        initialState = State(self.initialState, self.wordLengths)

        # Generate all root states
        rootStates = []
        for root in initialState.getValidRoots(self.trie):
                for path in root.getValidPaths(self.trie, initialState):
                    rootStates.append(initialState.getRemovedPathState(path))

        # Split root states up evenly to distribute to processes
        splitStates = [rootStates[i::numProcesses] for i in range(numProcesses)]

        # Create Solving Workers and delegate them work
        for i in range(numProcesses):
            p = Process(target=self.SolvingWorker, args=(i, splitStates[i], solutionQueue))
            self.processes.append(p)
            p.daemon = True
            p.start()

        # Keep looping while there are workers alive
        while True:
            solution = solutionQueue.get(1)

            # If there's no solution, check there are still workers alive, else exit
            if solution is None:
                # TODO(mitch): fix this. it infinite loops when all processes are done
                if all([not p.is_alive() for p in self.processes]):
                    break

                continue

            # Check if was a death message
            if type(solution) == int:
                self.processes[solution].terminate()
                self.processes[solution].join()
                continue

            # Check solution doesn't contain any bad words
            if not solution.words.isdisjoint(self.badWords):
                continue

            yield solution
