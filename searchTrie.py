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

# Log reason for quitting and quit
def quit(reason):
    logger.critical(reason)
    sys.exit(0)

# Solve the current board state
def solveState(state, trie, currentPath=[]):
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

    return solutionPaths

# Solve the current level
def solveLevel(state, wordLengths):
    # Create level state
    levelState = State(state, wordLengths)

    # Check .pickle file
    if not os.path.exists('words.pickle'):
        quit('Must generate a words.pickle file')

    # Load .pickle file
    logger.debug('Loading in Trie from words.pickle')
    with open('words.pickle', 'rb') as f:
        trie = pickle.load(f)

    # Check Trie was valid
    if trie is None:
        quit('There was a problem loading in the .pickle file')

    # Solve the given state
    return solveState(levelState, trie)