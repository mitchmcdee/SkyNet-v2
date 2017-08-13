import numpy as np
import logging
import cv2
from PIL import Image
import os.path

class GameCompleteCV:
    def __init__(self):
        self.BG_VALUE = 27
        self.THRESHOLD = 100
        self.MAX = 255
        self.TEST_DIR = os.path.join(os.path.dirname(__file__), 'test/')

    def image_to_gameover(self, image):
        pass
        img = np.array(image)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return  self.cv_check_gameover(img)
    def filename_to_gameover(self, filename_str):
        img = cv2.imread(filename_str, 0)
        return self.cv_check_gameover(img)

    def cv_check_gameover(self, img):
        height, width = img.shape
        logging.info("Height: " + str(height))
        logging.info("Width: " + str(width))
        ret,thresh = cv2.threshold(img,190,255, cv2.THRESH_BINARY)
        ratio = cv2.countNonZero(thresh) / float((height * width))
        print(ratio)
        return ratio < 0.08


def main():
    cv = GameCompleteCV()
    cv.filename_to_gameover(cv.TEST_DIR + "wordbrain3.jpg")
    cv.filename_to_gameover(cv.TEST_DIR + "gameover.jpg")
    cv.filename_to_gameover(cv.TEST_DIR + "gameover2.jpg")
    cv.filename_to_gameover(cv.TEST_DIR + "gameover3.jpg")

    


if __name__ == "__main__": main()
# Load an color image in grayscale
