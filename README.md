# SkyNet-v2
SkyNet v2 is an AI designed to autonomously play the popular mobile game 'Word Brain'. It was built in Python 3 using PyOpenCV for reading board state, PyTesseract for Optical Character Recognition and PyAutoGUI for autonomous input into the BlueStacks android emulator.

The AI generates a tailored trie tree from a dictionary of words and uses it to cross check potential solutions during the search process. Multi-processing is used to parallelise the search, and potential solutions are yielded and tested asynchronously to further reduce the search space by eliminating bad words.

SkyNet v2 is an ongoing project, and will hopefully reach a state in which it is able to complete the entire game autonomously.

Team SkyNet v2 took second place at the 2017 Code Network Hackathon.
