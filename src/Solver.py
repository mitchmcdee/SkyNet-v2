import sys
import os
from Trie import Trie, TrieNode
from State import State, StateNode

class Solver:
    def __init__(self, wordLengths):
        self.solutions = []
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

    #TODO(mitch): check level 4 of rat

    # Solve the current level
    def solveLevel(self, initialState, wordLengths):
        solutions = []
        unsolvedStates = [State(initialState, wordLengths)]
        while len(unsolvedStates) != 0:
            state = unsolvedStates.pop()

            if len(state.wordLengths) == 0:
                solutions.append(state.path)

            validPaths = []
            for root in state.getValidRoots(self.trie):
                validPaths.extend(root.getValidPaths(self.trie, state))

            for path in validPaths:
                unsolvedStates.append(state.getRemovedPathState(path))

        return solutions
