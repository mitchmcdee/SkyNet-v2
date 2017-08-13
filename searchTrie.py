import pickle
import logging
import sys
import os
from Trie import Trie, TrieNode
from State import State, StateNode
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
TEST_STATE = State(['e','n','r','d','l','o','c','o','h','b','a','t','r','t','r','e'], [6,5,5])
# TEST_STATE = State(['s','i','o','s','h','t','m','r','k','c','r','o','a','a','t','t','h','n','e','a','b','a','p','p','f'], [5,3,3,8,6])
# TEST_STATE = State(['b','g','r','t','e','k','l','a','e','e','r','c','c','t','r','w','h','i','t','e','r','e','o','b','u','e','r','s','h','g','b','i','r','g','l','i'], [6,7,6,7,5,5])

# Log reason for quitting and quit
def quit(reason):
    logger.critical(reason)
    sys.exit(0)

# Solve the current board state
def solveState(state, trie, currentPath=[]):
    # logger.debug("Solving " + str(state.state))

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
        rv = solveState(state.getRemovedWordState(path), trie, currentPath + [path])
        (solutionPaths.extend(rv) if rv else None)

    # Ignore this lol. Removes all duplicate solution paths
    return list(set(tuple([tuple(map(tuple, s)) for s in solutionPaths])))

# Check file
if len(sys.argv) == 1 or not os.path.exists(sys.argv[1]):
    print('Must provide a valid .pickle file')
    sys.exit(0)

# Load .pickle file
logger.debug('Loading in .pickle trie')
with open(sys.argv[1], 'rb') as f:
    trie = pickle.load(f)

if trie is None:
    quit('There was a problem loading in the .pickle file')

# Solve the given state
print(solveState(TEST_STATE, trie))