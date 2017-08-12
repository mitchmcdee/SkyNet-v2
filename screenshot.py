#!/bin/python
import pyautogui, time



def screenshot(left, top, width, height):
	width = width - left
	height = height - top
	region = ()

	im = pyautogui.screenshot(region=(left, top, width, height))
	im.show()
	
time.sleep(3)
cursorX, cursorY = pyautogui.position()
screenshot(0, 13, cursorX, cursorY)
