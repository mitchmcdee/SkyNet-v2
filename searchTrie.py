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


# TEST_STATE = State(['a','b','l','e'])
# TEST_WORD_LENS = [4]


TEST_STATE = State(['e','s','t','g','i','e','g','n','n'])
TEST_WORD_LENS = [6, 3]


# TEST_STATE = State(['b','g','o','p','c','a','n','m','d','h','i','j','e','f','k','l'])
# TEST_WORD_LENS = [6,4,3,3]


def quit(reason):
    logger.critical(reason)
    sys.exit(0)


def solveState(state, currentPath, wordLengths):
    # logger.debug("Solving " + str(state.state))

    if len(wordLengths) == 0:
        return [currentPath]

    validPaths = []
    for r in state.getPathRoots():
        paths = r.getValidPaths(t, state, wordLengths[0])
        (validPaths.extend(paths) if paths is not None else None)

    if len(validPaths) == 0:
        return None

    solvedStates = []
    for path in sorted(validPaths, key=lambda x: len(x)):
        rv = solveState(state.getRemovedWordState(path), currentPath + [path], wordLengths[1:])
        (solvedStates.extend(rv) if rv is not None else None)

    return solvedStates


logger.debug('Checking words.pickle exists')
if os.path.exists('words.pickle') is not True:
    quit('Could not find words.pickle')

logger.debug('Loading in words.pickle trie')
with open('words.pickle', 'rb') as f:
    t = pickle.load(f)

if t is None:
    quit('There was a problem loading in the pickle file')

print(solveState(TEST_STATE, [], TEST_WORD_LENS))