#!/bin/python
import pyautogui, sys, time

def selectWords(listOfWords, speed = 0.1):
	
	for word in listOfWords:

		#move to the start of the word before selecting anything
		pyautogui.moveTo(word[0][0], word[0][1], speed)

		#press mouse down for the entire mouse moving sequence
		pyautogui.mouseDown()

		for letter in word:

			pyautogui.moveTo(letter[0], letter[1], speed)

		pyautogui.mouseUp()