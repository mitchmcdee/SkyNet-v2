import sys
from math import sqrt
from copy import deepcopy

# Possible neighbour directions of each node in a State
directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

# Log reason for quitting and quit
def quit(reason):
    logger.critical(reason)
    sys.exit(0)

# State of
class State():
    def __init__(self, state, wordLengths):
        # Side length of the (hopefully) perfect square
        sideLength = sqrt(len(state))

        # Check input state is a perfect square
        if (sideLength != int(sideLength)):
            quit("Input state is not a perfect square")

        # Check all chars are valid
        if not all([str(c).isalpha() or c == '_' for c in state]):
            quit("Input contains illegal chars")

        # Check word lengths are valid
        if len(state) != sum(wordLengths):
            quit("Input contains invalid word lengths")

        self.state = state
        self.sideLength = int(sideLength)
        self.wordLengths = wordLengths

    # Returns all the children surrounding a given point
    def getChildrenFromPoint(self, pointIndex):
        children = []

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

            # Append it as a valid child
            children.append(childIndex)

        return children

    # Generates and returns a list of valid (i.e. can make a word) root nodes
    def getValidRoots(self, trie):
        roots = []

        # Loop over each of the top level nodes in a state
        for i,v in enumerate(self.state):
            # Skip over whitespaces (words don't start with whitespace)
            if v == '_':
                continue

            root = StateNode(i, self.state[i], {}, [self.state[i]])
            stack = [root]

            # Perform simple DFS on each path
            while len(stack) != 0:
                current = stack.pop()

                # Loop over possible children
                for c in self.getChildrenFromPoint(current.index):
                    # Avoid cycle
                    if c in current.parents:
                        continue

                    childPath = deepcopy(current.path) + [self.state[c]]

                    # Check path is a valid path (i.e. can make a word)
                    if trie.isPath(childPath) is not True:
                        continue

                    child = StateNode(c, self.state[c], deepcopy(current.parents), childPath)
                    child.addParent(current)
                    current.addChild(child)
                    stack.append(child)

            roots.append(root)

        return roots

    # Print out the State in a nice grid
    def printState(self):
        for i in range(self.sideLength):
            multiplier = i * self.sideLength
            print(self.state[multiplier : self.sideLength + multiplier])

    # Return the word translation of the given path
    def getWord(self, path):
        return ('').join([self.state[i] for i in path])

    # Generate and return a new State that removes the given word
    def getRemovedWordState(self, path):
        newState = deepcopy(self)

        # Replace path with underscores (i.e. empty space)
        for i in path:
            newState.state[i] = '_'

        # If tiles need to be dropped down, do so
        for i in range(len(newState.state)):
            if newState.state[i] != '_':
                continue

            # swap cells all the way up
            aboveCellIndex = i - self.sideLength
            while aboveCellIndex >= 0:

                temp = newState.state[i]
                newState.state[i] = newState.state[aboveCellIndex]
                newState.state[aboveCellIndex] = temp

                aboveCellIndex -= self.sideLength
                i -= self.sideLength

        # Remove word length of word that was removed
        newState.wordLengths.remove(len(path))
        
        return newState


# State Nodes are nodes contained in the valid paths of a State
class StateNode():
    def __init__(self, index, value, parents, path):
        self.index = index
        self.value = value
        self.parents = parents
        self.children = {}
        self.path = path

    # Add a childd to the State Node
    def addChild(self, child):
        self.children[child.index] = child


    # Add a parent to the State Node
    def addParent(self, parent):
        self.parents[parent.index] = None

    # Print out all the children in a path
    def printChildren(self):
        print(self.value, self.children)
        for child in self.children.values():
            printChildren(child)

    # Return all the possible paths for a State Node
    def getPaths(self):
        paths = [[self.index]]
        for child in self.children.values():
            paths.extend([[self.index] + child for child in child.getPaths()])
    
        return paths

    # Return all the valid paths (i.e. paths that make a word of the required length)
    def getValidPaths(self, trie, state):
        return list(filter(lambda x: len(x) in state.wordLengths and trie.isWord(state.getWord(x)), self.getPaths()))

