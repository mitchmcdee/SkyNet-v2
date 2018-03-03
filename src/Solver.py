import os
import logging
import queue
from collections import Counter
from multiprocessing import Process, Queue, Manager
from state import State
from trie import Trie

LOGGER = logging.getLogger(__name__)
HANDLER = logging.FileHandler('workers.log')
FORMATTER = logging.Formatter('%(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)


# Generates a trie tailored to the given state and word lengths and broadcasts it
def initialise_trie(state, word_lengths):
    trie = Trie()
    with open('../resources/goodWords.txt', 'r') as word_file:
        for line in word_file:
            word = line.strip('\n')

            # Skip words that have lengths not of interest
            if len(word) not in word_lengths:
                continue

            state_counter = Counter(state)
            word_counter = Counter(word)
            state_counter.subtract(word_counter)

            # Skip words that cannot be made from the initial state of letters
            if any(v < 0 for v in state_counter.values()):
                continue

            trie.add_word(word)

    num_words = len(trie.words)
    LOGGER.info(f'Added {num_words} words to trie')
    return trie


class Solver:
    SEEN_THRESHOLD = 25 # Minimum state size that will yield any new words seen

    def __init__(self):
        manager = Manager()                 # TODO(mitch): profile this and see if its performant?
        self.bad_words = manager.dict()     # Set of words not to search
        self.seen_words = manager.dict()    # Set of words already seen
        self.tested_words = manager.dict()  # Set of words already tested
        self.workers = []                   # List of workers

        self.solution_queue = Queue()
        self.test_queue = Queue()
        self.death_queue = Queue()

        self.trie = None

    # Return self on enter
    def __enter__(self):
        return self

    # Clear queues and words on exit
    def __exit__(self, type_, val, trace_back):
        for worker in self.workers:
            worker.terminate()
            worker.join()

    # Add a bad word to avoid it being searched again
    def add_bad_word(self, word):
        self.bad_words[word] = 1

    # Add a seen word to avoid it being tested again
    def add_tested_word(self, word):
        self.tested_words[word] = 1

    # Solve the current level
    def get_solutions(self, state, word_lengths):
        # Initialise trie tree
        self.trie = initialise_trie(state, word_lengths)

        # Generate all root states
        initial_state = State(state, word_lengths)
        root_states = self.get_child_states('pre:', initial_state)

        # Split root states up evenly to distribute to processes
        num_workers = os.cpu_count() - 1
        split_states = [root_states[i::num_workers] for i in range(num_workers)]

        # Start workers
        for i in range(num_workers):
            process = Process(target=self.solver_worker, args=(i, split_states[i]))
            process.daemon = True
            process.start()
            self.workers.append(process)

        # Yield found solutions
        active_workers = num_workers
        while True:
            # Check for dead workers
            try:
                worker_id = self.death_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                process = self.workers[int(worker_id)]
                process.terminate()
                process.join()
                active_workers -= 1
                LOGGER.info(f'{active_workers} workers left!')

            # Check for complete solutions
            try:
                solution_state = self.solution_queue.get_nowait()
            except queue.Empty:
                # If no more solutions and no more workers, exit
                if active_workers == 0:
                    break
            else:
                if set(solution_state.words).isdisjoint(self.bad_words.keys()):
                    yield solution_state

            # Check for test solutions
            try:
                test_word, test_state = self.test_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                if test_word not in self.tested_words and set(test_state.words).isdisjoint(self.bad_words.keys()):
                    yield test_state
                if test_word in self.seen_words:
                    del self.seen_words[test_word]

    # Worker which solves states and sends solutions to main process
    def solver_worker(self, i, stack):
        while len(stack) != 0:
            state = stack.pop()

            # Check state doesn't contain any bad words
            if not set(state.words).isdisjoint(self.bad_words.keys()):
                continue

            # Calculate child states
            stack.extend(self.get_child_states(i, state))

        # Send death message
        self.death_queue.put(i)

    # Generates all child solutions of a root state
    def get_child_states(self, i, state):
        child_states = []
        unique_states = set()
        for path in state.get_valid_paths(self.trie):
            # If the child word already exists, skip over the state
            child_word = state.get_word(path)
            if child_word in state.words:
                continue

            # If the child state already exists, skip over the state
            child_state = state.get_removed_path_state(path)
            if tuple(child_state.state) in unique_states:
                continue

            # If there are no more words, we've found a complete solution
            if len(child_state.word_lengths) == 0:
                self.solution_queue.put(child_state)
                continue

            child_states.append(child_state)
            unique_states.add(tuple(child_state.state))
            LOGGER.info(f'{i}: {child_state.words}')

            # If we're solving a small state, don't bother testing solutions
            if len(child_state.state) <= Solver.SEEN_THRESHOLD:
                continue

            # If we haven't seen a word before, test it
            for word in child_state.words:
                if word not in self.seen_words and word not in self.tested_words:
                    self.seen_words[word] = 1
                    self.test_queue.put((word, child_state))
                    # LOGGER.info(f'{i}: {word} {child_state.words}')
                    break
        return child_states
