import sys
from math import sqrt

# Possible neighbour directions of each node in a State
directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]


# State of
class State():
    def __init__(self, state, wordLengths, path=[], words=set(), allStates=None):
        self.state = state
        self.sideLength = int(sqrt(len(state)))
        self.wordLengths = wordLengths
        self.path = path
        self.words = words
        self.allStates = allStates or [state]

    # Returns all the children surrounding a given point
    def getChildrenFromPoint(self, pointIndex):
        # Iterate over each direction
        for child in directions:
            # Convert 1D indexing to x and y coords
            childX = pointIndex % self.sideLength + child[0]
            childY = pointIndex // self.sideLength + child[1]

            # Check whether it's a valid point
            if childX < 0 or childY < 0 or childX >= self.sideLength or childY >= self.sideLength:
                continue

            # Calculate index of the child
            childIndex = childX + childY * self.sideLength

            # Skip over children which are underscores (i.e. empty space)
            if self.state[childIndex] == '_':
                continue

            yield childIndex

    # Generates and returns a list of valid (i.e. can make a word) root nodes
    def getValidRoots(self, trie):
        # Loop over each of the top level nodes in a state
        for i, v in enumerate(self.state):
            # Skip over whitespaces (words don't start with whitespace)
            if v == '_':
                continue

            root = StateNode(i, self.state[i], set(), [self.state[i]])
            stack = [root]

            # Perform simple DFS on each path
            while len(stack) != 0:
                current = stack.pop()

                # Loop over possible children
                for c in self.getChildrenFromPoint(current.index):
                    # Avoid cycle
                    if c in current.parents:
                        continue

                    childPath = current.path[:] + [self.state[c]]

                    # Check path is a valid path (i.e. can make a word)
                    if not trie.isPath(childPath):
                        continue

                    childParents = current.parents.copy()
                    childParents.add(current.index)

                    child = StateNode(c, self.state[c], childParents, childPath)
                    current.addChild(child)

                    stack.append(child)

            yield root

    # Return the word translation of the given path
    def getWord(self, path):
        return ''.join([self.state[i] for i in path])

    # Generate and return a new State that removes the given path
    def getRemovedPathState(self, path):
        newState = self.state[:]

        # Replace path with underscores (i.e. empty space)
        for i in path:
            newState[i] = '_'

        # If tiles need to be dropped down, do so
        for i, v in enumerate(newState):
            if v != '_':
                continue

            # swap cells all the way up
            aboveCellIndex = i - self.sideLength
            while aboveCellIndex >= 0:
                newState[i], newState[aboveCellIndex] = newState[aboveCellIndex], v
                aboveCellIndex -= self.sideLength
                i -= self.sideLength

        newWordLengths = self.wordLengths[:]
        newWordLengths.remove(len(path))

        newWords = self.words.copy()
        newWords.add(self.getWord(path))

        return State(newState, newWordLengths, self.path[:] + [path], newWords, self.allStates[:] + [newState])

    # Returns whether the given path is valid one.
    def isValidPath(self, path, trie):
        return len(path) in self.wordLengths and trie.isWord(self.getWord(path))

    # Return all the valid paths (i.e. paths that make a word of the required length)
    def getValidPaths(self, trie):
        for root in self.getValidRoots(trie):
            for path in root.getPaths():
                if self.isValidPath(path, trie):
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
    def addChild(self, child):
        self.children[child.index] = child

    # Return all the possible paths for a State Node
    def getPaths(self):
        yield [self.index]
        for child in self.children.values():
            for path in ([self.index] + child for child in child.getPaths()):
                yield path