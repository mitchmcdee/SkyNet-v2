import pickle
import sys
import os
from Trie import Trie, TrieNode
from State import State, StateNode

class Solver:
    def __init__(self):
        # Check .pickle file
        if not os.path.exists('../resources/words.pickle'):
            print('Must generate a words.pickle file')
            sys.exit(0)

        # Load .pickle file
        with open('../resources/words.pickle', 'rb') as f:
            self.trie = pickle.load(f)

        # Check Trie was valid
        if self.trie is None:
            print('There was a problem loading in the .pickle file')
            sys.exit(0)

    # Solve the current board state
    def solveState(self, state, trie, currentPath=[]):
        # If there are no more word lengths, there's nothing left to solve
        if len(state.wordLengths) == 0:
            return [currentPath]

        # Loop over the root nodes and add their valid paths
        validPaths = []
        for r in state.getValidRoots(trie):
            paths = r.getValidPaths(trie, state)
            (validPaths.extend(paths) if paths else None)

        # Loop over the valid paths and add their solved states
        solutionPaths = []
        for path in validPaths:
            rv = self.solveState(state.getRemovedWordState(path), trie, currentPath + [path])
            (solutionPaths.extend(rv) if rv else None)

        return solutionPaths

    # Solve the current level
    def solveLevel(self, state, wordLengths):
        # Create level state
        levelState = State(state, wordLengths)

        # Solve the given state
        return self.solveState(levelState, self.trie)