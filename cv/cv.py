import numpy as np
import cv2

# Load an color image in grayscale
img = cv2.imread('wordbrain.jpg', 0)
height, width = img.shape
print(height)
print(width)
start_index = int(height * 0.15)
end_index = int(height * 0.85)
black_flag = true

star

for i in range(start_index, end_index):
    if print(img[i,20]) > 50 and black_flag:
        black_flag = False
    
cv2.waitKey(0)
cv2.destroyAllWindows()