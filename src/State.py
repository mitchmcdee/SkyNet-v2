import sys
from math import sqrt

# Possible neighbour directions of each node in a State
DIRECTIONS = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]


# State of
class State():
    def __init__(self, state, word_lengths, path=None, words=None, all_states=None):
        self.state = state
        self.side_length = int(sqrt(len(state)))
        self.word_lengths = word_lengths
        self.path = path or []
        self.words = words or set()
        self.all_states = all_states or [state]

    # Returns all the children surrounding a given point
    def get_children_from_point(self, point_index):
        # Iterate over each direction
        for child in DIRECTIONS:
            # Convert 1D indexing to x and y coords
            child_x = point_index % self.side_length + child[0]
            child_y = point_index // self.side_length + child[1]

            # Check whether it's a valid point
            if child_x < 0 or child_y < 0 or child_x >= self.side_length or child_y >= self.side_length:
                continue

            # Calculate index of the child
            child_index = child_x + child_y * self.side_length

            # Skip over children which are underscores (i.e. empty space)
            if self.state[child_index] == '_':
                continue

            yield child_index

    # Generates and returns a list of valid (i.e. can make a word) root nodes
    def get_valid_roots(self, trie):
        # Loop over each of the top level nodes in a state
        for i, char in enumerate(self.state):
            # Skip over whitespaces (words don't start with whitespace)
            if char == '_':
                continue

            root = StateNode(i, char, set(), [char])
            stack = [root]

            # Perform simple DFS on each path
            while len(stack) != 0:
                current = stack.pop()

                # Loop over possible children
                for child in self.get_children_from_point(current.index):
                    # Avoid cycle
                    if child in current.parents:
                        continue

                    child_path = current.path[:] + [self.state[child]]

                    # Check path is a valid path (i.e. can make a word)
                    if not trie.is_path(child_path):
                        continue

                    child_parents = current.parents.copy()
                    child_parents.add(current.index)

                    child_node = StateNode(child, self.state[child], child_parents, child_path)
                    current.add_child(child_node)

                    stack.append(child_node)

            yield root

    # Return the word translation of the given path
    def get_word(self, path):
        return ''.join([self.state[i] for i in path])

    # Generate and return a new State that removes the given path
    def get_removed_path_state(self, path):
        new_state = self.state[:]

        # Replace path with underscores (i.e. empty space)
        for i in path:
            new_state[i] = '_'

        # If tiles need to be dropped down, do so
        for i, char in enumerate(new_state):
            if char != '_':
                continue

            # swap cells all the way up
            above_cell_index = i - self.side_length
            while above_cell_index >= 0:
                new_state[i], new_state[above_cell_index] = new_state[above_cell_index], char
                above_cell_index -= self.side_length
                i -= self.side_length

        new_word_lengths = self.word_lengths[:]
        new_word_lengths.remove(len(path))

        new_words = self.words.copy()
        new_words.add(self.get_word(path))

        return State(new_state, new_word_lengths, self.path[:] + [path], new_words, self.all_states[:] + [new_state])

    # Returns whether the given path is valid one.
    def is_valid_path(self, path, trie):
        return len(path) in self.word_lengths and trie.is_word(self.get_word(path))

    # Return all the valid paths (i.e. paths that make a word of the required length)
    def get_valid_paths(self, trie):
        for root in self.get_valid_roots(trie):
            for path in root.get_paths():
                if self.is_valid_path(path, trie):
                    yield path


# State Nodes are nodes contained in the valid paths of a State
class StateNode:
    def __init__(self, index, value, parents, path):
        self.index = index
        self.value = value
        self.parents = parents
        self.children = {}
        self.path = path

    # Add a child to the State Node
    def add_child(self, child):
        self.children[child.index] = child

    # Return all the possible paths for a State Node
    def get_paths(self):
        yield [self.index]
        for child in self.children.values():
            for path in ([self.index] + child for child in child.get_paths()):
                yield path
