import numpy as np
import cv2
def calc_edges_h(start_index, end_index, offset):
    box_coords = []
    black_flag = True
    box_size = [0,0]
    for i in range(start_index, end_index):
        if img[i,20] > 50 and black_flag:
            black_flag = False
            box_size[0] = i
        elif img[i,20] < 50 and not black_flag:
            black_flag = True
            box_size[1] = i
            box_coords.append(box_size)
            box_size = [0,0]
    print(box_coords)
    return box_coords


def calc_edges_w(start_index, end_index, offset):
    box_coords = []
    black_flag = True
    box_size = [0,0]
    for i in range(start_index, end_index):
        if img[300,i] > 50 and black_flag:
            black_flag = False
            box_size[0] = i
        elif img[300,i] < 50 and not black_flag:
            black_flag = True
            box_size[1] = i
            box_coords.append(box_size)
            box_size = [0,0]
    print(box_coords)
    return box_coords
def calc_box_coords(width,height,w_offset,h_offset):
    start_index = int(height * 0.15)
    end_index = int(height * 0.85)
    box_coords_h = calc_edges_h(start_index, end_index,h_offset)
    start_index = 0
    end_index = int(width)
    box_coords_w = calc_edges_w(start_index, end_index,w_offset)

    return [((h[0],w[0]),(h[1],w[1])) for h in box_coords_h for w in box_coords_w]

# Load an color image in grayscale
img = cv2.imread('wordbrain.jpg', 0)
height, width = img.shape
print(height)
print(width)

box_coords = calc_box_coords(width,height,300,20)
print(box_coords)

cv2.waitKey(0)
cv2.destroyAllWindows()