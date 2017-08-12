import numpy as np
import cv2
BG_VALUE = 27

def calc_edges_h(image, start_index, end_index, offset):
    box_coords = []
    black_flag = True
    box_size = [0,0]
    for i in range(start_index, end_index):
        print(image[i,offset])
        if image[i,offset] > 50 and black_flag:
            black_flag = False
            box_size[0] = i
        elif image[i,offset] < 50 and not black_flag:
            black_flag = True
            box_size[1] = i
            box_coords.append(box_size)
            box_size = [0,0]
    print("height coords: " + str(box_coords))
    return box_coords


def calc_edges_w(image, start_index, end_index, offset):
    box_coords = []
    black_flag = True
    box_size = [0,0]
    for i in range(start_index, end_index):
        print(image[offset,i])
        if image[offset,i] > 200 and black_flag:
            black_flag = False
            box_size[0] = i
        elif image[offset,i] < 30 and not black_flag:
            black_flag = True
            box_size[1] = i
            box_coords.append(box_size)
            box_size = [0,0]
    print("width coords: " + str(box_coords))
    return box_coords

def calc_box_coords(image, width,height,horizontal_offset):
    start_index = int(height * 0.15)
    end_index = int(height * 0.85)
    box_coords_h = calc_edges_h(image, start_index, end_index,horizontal_offset)
    vertical_offset = box_coords_h[0][0] + 20 # first height coord in grid
    print("Vertical offset of grid: " + str(vertical_offset))
    start_index = 0
    end_index = int(width)
    box_coords_w = calc_edges_w(image, start_index, end_index,vertical_offset)
    return [((w[0],h[0]),(w[1],h[1])) for h in box_coords_h for w in box_coords_w]

def calc_midpoints(i_indexes):
    block_start = i_indexes[0]
    block_start_index = 0
    split_blocks = []
    midpoints = []

    prev = i_indexes[0] - 1
    prev_index = 0
    FORGIVENESS = 2 # Higher the value, the higher gaps we forgive between blocks
    length = len(i_indexes)
    for index, val in enumerate(i_indexes):
        if prev < (val - FORGIVENESS) or index == length - 1:
            #If we get here, then we have hit the start of a new block
            print("block start: " + str(block_start_index))
            print("block end: " + str(index-1))
            split_blocks.append(i_indexes[block_start_index:(index-1)])
            block_start_index = index
        prev = val
    for block in split_blocks:
        print(block)
        if len(block) < 3:
            continue
        midpoints.append(block[int(len(block)/2)])
    return midpoints
def calc_boxes(image, midpoints, width):
    for block in midpoints:
        double_lines = 0

        for j in range(width):


def calc_word_lengths(image,vert_offset,width, bottom):
    print("offset: " + str(vert_offset) + " bottom: " + str(bottom))
    i_indexes = []
    for i in range(vert_offset, bottom):
        bg_count = 0
        temp = []
        white_flag = False
        for j in range(width):
            temp.append(image[i,j])
            if (image[i,j]  > (BG_VALUE - 4)) and (image[i,j]  < (BG_VALUE + 4)):
                bg_count += 1
            if image[i,j] > 180:
                white_flag = True
        if (bg_count > (0.50*width)) and white_flag:
            i_indexes.append(i)
    print("scan indexs: " + str(i_indexes))
    mid_indexs = calc_midpoints(i_indexes)
    for i in mid_indexs:
        for j in range(width):
                image[i,j] = 255
    print ("midpoints: " + str(mid_indexs))
    cv2.imwrite('scan.png',image)

# Load an color image in grayscale
img = cv2.imread('wordbrain3.jpg', 0)
height, width = img.shape
print(height)
print(width)
box_coords = calc_box_coords(img,width,height,20)
mask = np.zeros((height,width,1), np.uint8)
lowest_point = 0
for rect in box_coords:
    cv2.rectangle(mask,rect[0], rect[1],255,1)
    lowest_point = lowest_point if (lowest_point > rect[1][1]) else rect[1][1]
res = cv2.addWeighted(mask,1,img,0.3,0)
print("end of grid: " + str(lowest_point))
vert_offset_word_boxes = lowest_point + 20
wordlengths = calc_word_lengths(img,vert_offset_word_boxes,width, int(height * 0.90))

print(box_coords)
cv2.imwrite('output.png',res)
cv2.waitKey(0)
cv2.destroyAllWindows()