#!/usr/bin/python3

import logging
import pickle
import sys
from trie import Trie, TrieNode


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

###################
# Trie Generating #
###################

MINWORDSIZE = 3

def genTrie(maxWords):
    t = Trie()

    numWords = 0
    longestWord = ''
    with open("words.txt", "r") as f:
        for i,w in enumerate(f):
            word = w.strip('\n')

            if len(word) < MINWORDSIZE:
                continue

            if i > maxWords:
                break

            if len(longestWord) != max(len(longestWord), len(word)):
                longestWord = word

            numWords += 1
            t.addToTrie(word)

    logger.debug("Longest word is '" + longestWord + "'' with length " + str(len(longestWord)))
    logger.debug("Total number of words is: " + str(numWords))

    with open('words.pickle', 'wb') as f:
        pickle.dump(t, f, pickle.HIGHEST_PROTOCOL)

    logger.debug("Trie generated!")


def validateTrie():
    with open('words.pickle', 'rb') as f:
        t = pickle.load(f)
        if isinstance(t, Trie):
            logger.debug("Trie is VALID")
            return t
        else:
            logger.critical("Trie is INVALID")


if len(sys.argv) >= 2 and sys.argv[1] == 'gen':
    numWords = int(sys.argv[2]) if (len(sys.argv) == 3) else sys.maxsize
    genTrie(numWords)

elif len(sys.argv) == 2 and sys.argv[1] == 'read':
    t = validateTrie()
    if t is not None:
        logger.debug("Longest word length in trie is: " + str(t.getMaxDepth(t.root)))

else:
    logger.critical("Must be 'gen' or 'read'")