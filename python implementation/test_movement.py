import numpy as np
import cv2

img = cv2.imread('stylized_map.png',1)

# Center coordinates
center_coordinates = (50, 50)

# Radius of circle
radius = 5

# Blue color in BGR
color = (250, 250, 250)

# Line thickness of 2 px
thickness = 1

i = 0
while True:
    center_coordinates = (50 + i, 50+(i*2))
    i+=1
    print(str(i))
    #kernel = np.array([[-1,-1,-1], [-1,10,-1], [-1,-1,-1]])
    #img = cv2.filter2D(img, -1, kernel)
    # Using cv2.circle() method
    # Draw a circle with blue line borders of thickness of 2 px
    image = img.copy()
    image = cv2.circle(image, center_coordinates, radius, color, thickness)


    cv2.imshow('image',image)
    k = cv2.waitKey(1)

    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()
