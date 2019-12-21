import numpy as np
import cv2
import csv

def is_valid(hei, wi, ro, co):
    if (wi > co and co >= 0 and hei > ro and ro >= 0):
        return True
    return False

def is_contained(pix, arr):
    for i in range(len(arr)):
        if (pix[0] == arr[i][0] and pix[1] == arr[i][1] and pix[2] == arr[i][2]):
            return i
    return -1

# Create array from all the found BOXES
def create_box_array(arr, boxes):
    w = arr.shape[0]
    h = arr.shape[1]
    new_arr = arr.copy()

    progress = 0
    progress_total = len(boxes)

    for box in boxes:
        progress += 1
        print("progress: " + str(progress) + " / " + str(progress_total))
        for x in range(box.x[0], (box.y[0])):
            for y in range(box.x[1], (box.y[1])):
                if(is_valid(h, w, y, x)):
                    if COLOR_ENCODED[box.order] == 5:
                        new_arr[x][y] = [50,100,150]
                    else:
                        new_arr[x][y] = COLOR_ENCODED[box.order]

    return new_arr



class DensityBox:
    def __init__(self, x_pos, y_pos, order):
        self.x = x_pos
        self.y = y_pos
        self.order = order


img = cv2.imread('black_white_blue.png',1)
image_new = img.copy()

width = image_new.shape[0]
height = image_new.shape[1]

kernel_blade_size = [5,5]

total_rows = int(height/kernel_blade_size[0])
total_cols = int(width/kernel_blade_size[1])

counter = 0

# Color in which is encoded density lowest to highst
# THE LAST COLOR IS THE BACKGROUND WE IGNORE
COLOR_ENCODED = [[0,0,0],[30,30,30],[110,110,110], [200,200,200], [255,255,255], [255,0,0]]
COLOR_ENCODED = [[255,255,255],[200,200,200], [110,110,110], [30,30,30],[0,0,0], [255,0,0]]
# List of all the density boxes
DensityBoxes = []

######################
##########DETECTING BOXXES
print("gathering boxes started")
######################

for i in range(total_rows):
    for j in range(total_cols):
        counter += 1
        # Count all different pixel groups and find the most used
        usage_of_colors = [0]*len(COLOR_ENCODED)

        for row in range(kernel_blade_size[0]):
            for col in range(kernel_blade_size[1]):

                col_pos = col + j*kernel_blade_size[1]
                row_pos = row + i*kernel_blade_size[0]

                if (is_valid(height, width, row_pos, col_pos)):
                    pixel = image_new[col_pos][row_pos]

                    # Find familiar pixels and count them
                    statement = is_contained(pixel, COLOR_ENCODED)
                    if(statement != -1):
                        usage_of_colors[statement] += 1

                    #image_new[col_pos][row_pos] = (counter,counter,counter)

        # choose the order of the boxes from most counted pixels
        # chceck if there is at least one non zero number



        index = usage_of_colors.index(max(usage_of_colors))

        # Save left upper corner as well as right down corner
        x_box_pos = [(j)*kernel_blade_size[1], (i)*kernel_blade_size[0]]
        y_box_pos =  [(j+1)*kernel_blade_size[1],(i+1)*kernel_blade_size[0]]
        DensityBoxes.append(DensityBox(x_box_pos,y_box_pos, index))
        #print("The most used is: " + str(index))


######################
##########DETECTING BOXXES
print("gathering boxes ended")
######################



######################
##########DETECTING BOXXES
print("editing image started")
######################

#EDITED IMAGE
edited_image = create_box_array(image_new, DensityBoxes)

######################
##########DETECTING BOXXES
print("editing image ended")
######################

# SAVE BOXES DATA TO CSV
# Save only valid boxes
#
with open('boxes.csv', mode='w',newline='') as boxes_file:
    boxes_writer = csv.writer(boxes_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for box in DensityBoxes:
        if box.order != 5:
            boxes_writer.writerow([str(box.x[0]), str(box.x[1]), str(box.y[0]),str(box.y[1]), str(box.order)])

    print("Density Boxes saved")

while True:


    cv2.imshow('image',edited_image)
    k = cv2.waitKey(1)

    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()
