#!/usr/bin/python3

import pickle
import logging
import sys
import os
from trie import Trie, TrieNode
from state import State, StateNode

#################
# Logging Setup #
#################

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Additionally log to stdout
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


##################
# Trie Searching #
##################

state = State(['a', 'b', 'l', 'e'])
words = [1]

def quit(reason):
    logger.critical(reason)
    sys.exit(0)

logger.debug('Checking words.pickle exists')
if os.path.exists('words.pickle') is not True:
    quit('Could not find words.pickle')
logger.debug('Found words.pickle')

logger.debug('Loading in words.pickle trie')
with open('words.pickle', 'rb') as f:
    t = pickle.load(f)

if t is None:
    quit('There was a problem loading in the pickle file')

logger.debug('Generating word list')
words = []
for i,_ in enumerate(state.state):

    root = StateNode(i, state.state[i], None)
    stack = [root]
    visited = set()

    while len(stack) != 0:
        current = stack.pop()

        for c in state.getChildrenFromPoint(current.index):
            if current.hasParent(c):
                continue

            child = StateNode(c, state.state[c], current)
            current.addChild(child)
            stack.append(child)

    words.extend(root.getWords())

logger.debug("Checking valid words")
for word in words:
    isWord = ('').join(word) + ' is '
    isWord += 'NOT ' if not t.isWord(word) else ''
    isWord += 'a word'
    logger.debug(isWord)



