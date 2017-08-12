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

TEST_STATE = State(['a', 'b', 'l', 'q', 'e', 'q', 'q', 'q', 'q'])
TEST_WORD_LENS = [1]


def quit(reason):
    logger.critical(reason)
    sys.exit(0)


def solveState(state):
    longestPaths = [r.getLongestPath() for r in state.getRoots() if t.isWord(TEST_STATE.getWordFromPath(r.getLongestPath()))]
    
    if len(longestPaths) == 0:
        print("NO GOODIES FOR YA")
        return

    for path in longestPaths:
        print(path)
        print(state.getRemovedWordState(path))


logger.debug('Checking words.pickle exists')
if os.path.exists('words.pickle') is not True:
    quit('Could not find words.pickle')

logger.debug('Loading in words.pickle trie')
with open('words.pickle', 'rb') as f:
    t = pickle.load(f)

if t is None:
    quit('There was a problem loading in the pickle file')

# logger.debug('Checking valid words')
# for word in sorted(TEST_STATE.getWords(), key=lambda x: len(x), reverse=True):
#     logger.debug(('').join(word) + ": " + str(t.isWord(word)))

logger.debug('Solving state')
solveState(TEST_STATE)


