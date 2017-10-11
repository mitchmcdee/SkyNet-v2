import sys
import os
import logging
import pickle
from math import ceil
from Trie import Trie
from State import State
from collections import Counter
from multiprocessing import Process, Queue, Lock, Manager

logger = logging.getLogger(__name__)
handler = logging.FileHandler('workers.log')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Solver:
    SEEN_THRESHOLD = 25 # Minimum state size that will yield any new words seen

    def __init__(self):
        self.solutionQueue = Queue()
        self.testQueue =     Queue()

        m = Manager()               # TODO(mitch): profile this and see if its performant?
        self.badWords   = m.dict()  # Set of words not to search
        self.seenWords  = m.dict()  # Set of words already see
        self.trieEvents = m.dict()  # Set of worker ids that trigger a 'new trie' event
        self.jobList =    m.list()  # List of jobs for workers

        # Start workers
        self.numWorkers = max(1, os.cpu_count() - 1)
        for i in range(self.numWorkers):
            args = (i, self.trieEvents, self.badWords, self.seenWords,
                    self.jobList, self.testQueue, self.solutionQueue)
            p = Process(target=solvingWorker, args=args)
            p.daemon = True
            p.start()

    # Return self on enter
    def __enter__(self):
        return self

    # Clear queues and words on exit
    def __exit__(self, t, v, traceback):
        try:
            while True:
                jobList.clear()
        except:
            pass

        try:
            while True:
                solutionQueue.get_nowait()
        except:
            pass

        try:
            while True:
                testQueue.get_nowait()
        except:
            pass

        self.badWords.clear()
        self.seenWords.clear()

    # Add a bad word to avoid it being searched again
    def addBadWord(self, word):
        self.badWords[word] = 1

    # Solve the current level
    def getSolutions(self, state, wordLengths):
        logger.info('Getting solutions')
        initialState = State(state, wordLengths)

        # Generate trie tree
        numWords = 0
        trie = Trie()
        with open('../resources/goodWords.txt', 'r') as f:
            for line in f:
                word = line.strip('\n')

                # Skip words that have lengths not of interest
                if len(word) not in wordLengths:
                    continue

                stateCounter = Counter(state)
                wordCounter = Counter(word)
                stateCounter.subtract(wordCounter)

                # Skip words that cannot be made from the initial state of letters
                if any(v < 0 for v in stateCounter.values()):
                    continue

                numWords += trie.addWord(word)
        logger.info(f'Added {numWords} words to trie')

        # Create pickle of trie for processes
        with open('trie.pickle', 'wb') as f:
            pickle.dump(trie, f, protocol=pickle.HIGHEST_PROTOCOL)

        # Let processes know there's an updated pickle file
        for i in range(self.numWorkers):
            self.trieEvents[i] = True

        # Generate all root states and fill job list
        self.jobList.extend(getChildStates('pre', trie, initialState, self.seenWords, self.testQueue, self.solutionQueue))

        # Start yielding found solutions
        while True:
            try:
                solution = self.solutionQueue.get_nowait()
            except:
                pass
            else:
                if solution is not None and all(w not in self.badWords for w in solution.words):
                    yield solution

            try:
                test = self.testQueue.get_nowait()
            except:
                pass
            else:
                if test is not None and all(w not in self.badWords for w in test.words):
                    yield test

# Worker which solves states and sends solutions to main process
def solvingWorker(i, trieEvents, badWords, seenWords, jobList, testQueue, solutionQueue):
    trie = None
    unfinishedJobs = []
    while True:
        # Get a job
        try:
            state = unfinishedJobs.pop()
        except:
            try:
                while True:
                    unfinishedJobs.append(jobList.pop())
                    logger.info('yep1 ' + str(len(jobList)))
            except:
                continue

        # Check for updated trie event
        if trieEvents[i]:
            with open('trie.pickle', 'rb') as f:
                trie = pickle.load(f)
            trieEvents[i] = False

        # Check state doesn't contain any bad words
        if any(w in badWords for w in state.words):
            continue

        # Ensure trie exists before continuing
        if trie is None:
            unfinishedJobs.append(state)
            continue

        # Calculate child states
        unfinishedJobs.extend(getChildStates(i, trie, state, seenWords, testQueue, solutionQueue))

        # If we have lots of jobs, give some away
        if len(unfinishedJobs) > 50 and len(jobList) < 10:
            jobList.append(unfinishedJobs.pop())
            logger.info('yep2 ' + str(len(unfinishedJobs)) + ' ' + str(len(jobList)))

# Generates all child solutions of a root state
def getChildStates(i, trie, rootState, seenWords, testQueue, solutionQueue):
    childStates = []
    for root in rootState.getValidRoots(trie):
        for path in root.getValidPaths(trie, rootState):
            childState = rootState.getRemovedPathState(path)
            childWord = rootState.getWord(path)

            # If there are no more words, we've found a complete solution
            if len(childState.wordLengths) == 0:
                solutionQueue.put(childState)
                continue

            # If we haven't seen the removed word before, test it
            if childWord not in seenWords and len(childState.state) > Solver.SEEN_THRESHOLD:
                testQueue.put(childState)
                seenWords[childWord] = 1

            # logger.info(f'{i}: {childState.words}')
            childStates.append(childState)
    return childStates