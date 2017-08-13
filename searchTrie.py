import pickle
import logging
import sys
import os
from trie import Trie, TrieNode
from state import State, StateNode
from copy import deepcopy
from itertools import chain


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

# TEST_STATE = State(['e','g','g','t','e','n','s','i','n'], [6,3])
# TEST_STATE = State(['d','o','o','r','r','a','p','o','a','o','b','u','l','v','c','f'], [8,4,4])
# TEST_STATE = State(['e','n','r','d','l','o','c','o','h','b','a','t','r','t','r','e'], [6,5,5])
# TEST_STATE = State(['s','i','o','s','h','t','m','r','k','c','r','o','a','a','t','t','h','n','e','a','b','a','p','p','f'], [5,3,3,8,6])
# TEST_STATE = State(['b','g','r','t','e','k','l','a','e','e','r','c','c','t','r','w','h','i','t','e','r','e','o','b','u','e','r','s','h','g','b','i','r','g','l','i'], [6,7,6,7,5,5])


def quit(reason):
    logger.critical(reason)
    sys.exit(0)


def solveState(state, currentPath=[]):
    # logger.debug("Solving " + str(state.state))

    if len(state.wordLengths) == 0:
        return [currentPath] if len(list(chain.from_iterable(currentPath))) == len(state.state) else None

    validPaths = []
    for r in state.getValidPathRoots(t):
        paths = r.getValidPaths(t, state)
        (validPaths.extend(paths) if paths else None)

    solvedStates = []
    for path in validPaths:
        rv = solveState(state.getRemovedWordState(path), currentPath + [path])
        (solvedStates.extend(rv) if rv else None)

    # Ignore this lol. Removes all duplicate solutions
    return list(set(tuple([tuple(map(tuple, s)) for s in solvedStates])))


logger.debug('Checking words.pickle exists')
if os.path.exists('words.pickle') is not True:
    quit('Could not find words.pickle')

logger.debug('Loading in words.pickle trie')
with open('words.pickle', 'rb') as f:
    t = pickle.load(f)

if t is None:
    quit('There was a problem loading in the pickle file')

print(solveState(TEST_STATE))