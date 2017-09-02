import sys
import os
from Trie import Trie, TrieNode
from State import State, StateNode

class Solver:
    def __init__(self, initialState, wordLengths, badWords = []):
        self.badWords = set()               # Set of words not to search
        self.initialState = initialState    # Initial state of board
        self.wordLengths = wordLengths      # List of word lengths to look for

        # Generate Trie
        self.trie = Trie()
        numWords = 0
        # with open('../resources/bigWords.txt', 'r') as f:
        with open('../resources/goodWords.txt', 'r') as f:
            for line in f:
                word = line.strip('\n')

                if len(word) not in self.wordLengths:
                    continue

                numWords += self.trie.addWord(word)

        print('Added ' + str(numWords) + ' words to trie')

    # Add a bad word to avoid it being searched again
    def addBadWord(self, word):
        self.badWords.add(word.lower())

    # Solve the current level
    def solveLevel(self):
        unsolvedStates = [State(self.initialState, self.wordLengths)]
        while len(unsolvedStates) != 0:
            state = unsolvedStates.pop()

            if not state.words.isdisjoint(self.badWords):
                continue

            print(state.words)
            if len(state.wordLengths) == 0:
                yield state

            validPaths = []
            for root in state.getValidRoots(self.trie):
                validPaths.extend(root.getValidPaths(self.trie, state))

            for path in validPaths:
                unsolvedStates.append(state.getRemovedPathState(path))
