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
    def solveLevel(self, state, wordLengths):
        solutions = []
        options = [(State(state, wordLengths), [])]
        while len(options) != 0:
            option, currentPath = options.pop()

            if len(option.wordLengths) == 0:
                solutions.append(currentPath)

            validPaths = []
            for root in option.getValidRoots(self.trie):
                paths = root.getValidPaths(self.trie, option)
                (validPaths.extend(paths) if paths else None)

            for path in validPaths:
                options.append((option.getRemovedPathState(path), currentPath + [path]))

        return solutions
