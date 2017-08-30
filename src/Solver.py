import sys
import os
from Trie import Trie, TrieNode
from State import State, StateNode

class Solver:
    def __init__(self, wordLengths):
        # Generate Trie
        self.trie = Trie()
        numWords = 0
        for length in list(set(wordLengths)):
            print('Adding words of length ', length)
            # Loop over words in the file an add them to the Trie
            with open('../resources/' + str(length) + '.txt', 'r') as f:
                for word in f:
                    numWords += self.trie.addWord(word.strip('\n'))
        print('Added ', numWords, ' words to trie')

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