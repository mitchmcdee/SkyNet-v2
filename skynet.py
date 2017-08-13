import pyautogui, time
from cv import WordbrainCv

def screenshot(left, top, width, height):
    width = width - left
    height = height - top
    region = ()

    im = pyautogui.screenshot(region=(left, top, width, height))
    return im
charlie_coords = [5, 81, 983, 1825]
coord = charlie_coords
pil_image = screenshot(coord[0], coord[1], coord[2], coord[3])
cv = WordbrainCv()
letters, midpoints, wordlengths = cv.image_to_state(pil_image)
print(letters)
print(midpoints)
print(wordlengths)

