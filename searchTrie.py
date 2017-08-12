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

def quit(reason):
    logger.critical(reason)
    sys.exit(0)

TEST_STATE = State(['a', 'b', 'l', 'e'])
TEST_WORD_LENS = [1]

logger.debug('Checking words.pickle exists')
if os.path.exists('words.pickle') is not True:
    quit('Could not find words.pickle')
logger.debug('Found words.pickle')

logger.debug('Loading in words.pickle trie')
with open('words.pickle', 'rb') as f:
    t = pickle.load(f)

if t is None:
    quit('There was a problem loading in the pickle file')
logger.debug('Loaded trie successfully')

logger.debug('Generating word list')
words = TEST_STATE.getWords()

logger.debug("Checking valid words")
for word in words:
    logger.debug(('').join(word) + ": " + str(t.isWord(word)))



