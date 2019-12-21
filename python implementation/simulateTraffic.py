import numpy as np
import cv2
from math import cos, atan, sin
from PIL import ImageFont, Image, ImageDraw
import csv

import simulationCore
LOADED_BOXES = simulationCore.loaded_boxes

#*****************************************************
################# PARAMETERS #########################

# MINIMAL DISTANCE BETWEEN CHOSEN VEHICLES IN PIXELS
MINIMAL_DISTANCE = 150 # About 4.5 km
# TOTAL VEHICLES IN PRAGUE
TOTAL_VEHICLES = 851000
# PERCENTAGE OF USED VEHICLES FROM TOTAL AT THAT DAY *70%
PERCENTAGE_USED_VEHICLES = 0.8
# PERCENTAGE OF FLYING CARS *1%
PERCENTAGE_FLYING_CARS = 0.01
# PERCENTAGE OF FLYING CARS USED AT NOON
PERCENTAGE_FLYING_CARS_NOON = 0.87

#*****************************************************
#TOTAL FLYING CARS MORNING/AFTERNOON
FLYING_CARS = (TOTAL_VEHICLES*PERCENTAGE_USED_VEHICLES)*PERCENTAGE_FLYING_CARS

#FLYING VEHICLES USED NOON
FLYING_CARS_NOON = FLYING_CARS*PERCENTAGE_FLYING_CARS_NOON

# we calculate the span of time in minutes we have available and divide the cars accordingly
MORNING_BORDER = simulationCore.GLOBAL_TIME_CHANGE_EQUAL
NOON_BORDER = simulationCore.GLOBAL_TIME_CHANGE_REVERSE
AFTERNOON_BORDER = simulationCore.GLOBAL_TIME_END_TIME

DURATION_MORNING = (MORNING_BORDER - simulationCore.GLOBAL_TIME)/60
DURATION_NOON = (NOON_BORDER - simulationCore.GLOBAL_TIME_CHANGE_EQUAL)/60
DURATION_AFTERNOON = (AFTERNOON_BORDER - simulationCore.GLOBAL_TIME_CHANGE_REVERSE)/60

#VEHICLES PER MINUTE MORNING
Vehicles_pm_M = FLYING_CARS/DURATION_MORNING
#VEHICLES PER MINUTE NOON
Vehicles_pm_N = FLYING_CARS_NOON/DURATION_NOON
#VEHICLES PER MINUTE AFTERNOON
Vehicles_pm_AN = FLYING_CARS/DURATION_AFTERNOON
VEHICLES_FLOWN = 0



## DATA TO BE SAVED IN CSV ##
VEHICLES_INFO = [[], [], []] #Morning Noon Afternoon
WAS_SAVED = False

class Vehicle:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.end_x = end_x
        self.end_y = end_y

        #CAR SPEED PIXELS/SEC
        self.speed = .7

        # WHERE TO MOVE
        if ((end_x - start_x) > 0):
            self.way_x = 1
        else:
            self.way_x = -1

        if ((end_y - start_y) > 0):
            self.way_y = 1
        else:
            self.way_y = -1

        # X,Y speed from trigonometry
        delta_y = end_y-start_y
        delta_x = end_x-start_x
        if(delta_x == 0):
            delta_x = 0.000000001

        angle = atan(abs(delta_y)/abs(delta_x))
        self.speed_y = abs(self.speed * sin(angle))
        self.speed_x = abs(self.speed * cos(angle))

    def finished(self):
        counter = 0
        if ((self.way_x > 0) and ((self.end_x - self.current_x) <= 0)):
            counter += 1
        elif ((self.way_x < 0) and ((self.end_x - self.current_x) >= 0)):
            counter += 1

        if ((self.way_y > 0) and ((self.end_y - self.current_y) <= 0)):
            counter += 1
        elif((self.way_y < 0) and ((self.end_y - self.current_y) >= 0)):
            counter += 1

        if counter >= 2:
            return True
        return False


    def move(self):
        if (not self.finished()):
            self.current_x += (self.way_x*self.speed_x)
            self.current_y += (self.way_y*self.speed_y)



# if time (*1 minute) passes spawn vehicles
def spawn_vehicles(spawner):
    # current time
    current_time = simulationCore.GLOBAL_TIME

    global MORNING_BORDER, NOON_BORDER, AFTERNOON_BORDER, MINIMAL_DISTANCE, LOADED_BOXES, VEHICLES_FLOWN

    spawn_per_minute = 0

    csv_array_index = 0
    if current_time < MORNING_BORDER:
        spawn_per_minute = Vehicles_pm_M
    elif current_time < NOON_BORDER:
        spawn_per_minute = Vehicles_pm_N
        csv_array_index = 1
    elif current_time < AFTERNOON_BORDER:
        spawn_per_minute = Vehicles_pm_AN
        csv_array_index = 2

    for i in range(int(spawn_per_minute)):
        points = simulationCore.pick_start_end_point(LOADED_BOXES, MINIMAL_DISTANCE)
        if points != -1:
            new_vehicle = Vehicle(points[0][1], points[0][0], points[1][1], points[1][0])  # start_x, start_y, end_x, end_y
            spawner.append(new_vehicle)
            VEHICLES_FLOWN += 1

            #save info about vehicles to csv array
            global VEHICLES_INFO
            VEHICLES_INFO[csv_array_index].append([current_time, points[0][1], points[0][0], points[1][1], points[1][0]])


#img = cv2.imread('black_white_blue.png',1)
img = cv2.imread('stylized_map.png',1)

# CIRCLES SETTTINGS
# Center coordinates
center_coordinates = (50, 50)
# Radius of circle
radius = 2
#
radius_start_end = 1
# Blue color in BGR
#color = (250, 250, 250)
# Line thickness of 2 px
thickness = 2
thickness_start_end = 1

# TEXT SETTINGS
font = ImageFont.truetype("roboto_thin.ttf", 40)
#font                   = cv2.FONT_HERSHEY_SIMPLEX
coord_text_city = (70,70)
coord_text_vehicles = (70,120)
coord_text_vehicles_flown = (70,170)
coord_text_time = (70,220)
fontScale              = 1
fontColor              = (255,255,255)
lineType               = 2



i = 0

spawner = []
while True:
    simulationCore.tick_clock()

    image = img.copy()

    current_time = simulationCore.GLOBAL_TIME
    if(current_time % 60 == 1):
        spawn_vehicles(spawner)
    spawned_to_be_deleted = []

    for i in range(len(spawner)):
        if(not spawner[i].finished()):
            image = cv2.circle(image, (int(spawner[i].start_x), int(spawner[i].start_y)), radius_start_end, (255, 0, 255),thickness_start_end)
            image = cv2.circle(image, (int(spawner[i].end_x), int(spawner[i].end_y)), radius_start_end, (0, 0, 255),thickness_start_end)
            image = cv2.circle(image, (int(spawner[i].current_x), int(spawner[i].current_y)), radius, (0, 245, 245), thickness)

            image = cv2.circle(image, (460,285), 3, (0, 0, 245),2)
            spawner[i].move()
        else:
            #print("DELETE THIS ONE")
            spawned_to_be_deleted.append(i)

    for i in range(len(spawned_to_be_deleted)):
        del spawner[spawned_to_be_deleted[i]]

    ######### DRAWIN WITH CUSTOM FONT HELP FROM PIL lib
    # From OpenCV to Pil
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    draw = ImageDraw.Draw(pil)

    draw.text(coord_text_city, ("City: Prague"), font=font, fill=(235, 235, 235))
    draw.text(coord_text_vehicles, ("Flying: " + str(len(spawner))), font=font, fill=(235, 235, 235))

    #FORMAT THE TEXT
    flown = str(VEHICLES_FLOWN)
    if VEHICLES_FLOWN >= 1000000:
        flown = flown[0:-6] + " " + flown[-6:-3] + " " + flown[-3:-1] + flown[-1]
    elif VEHICLES_FLOWN >= 1000:
        flown = flown[0:-3] + " " + flown[-3:-1] + flown[-1]
    draw.text(coord_text_vehicles_flown, ("Flown: " + str(flown)), font=font, fill=(235, 235, 235))

    hours = simulationCore.GLOBAL_TIME_HOURS
    minutes = simulationCore.GLOBAL_TIME_MINUTES
    if int(minutes) < 10:
        minutes = "0" + str(minutes)

    draw_time = str(hours + ":" + minutes)
    draw.text(coord_text_time, draw_time, font=font, fill=(255, 255, 255))
    # From Pil to OpenCV
    cv2_img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    ########################################################

    cv2.imshow('image', cv2_img)

    time = simulationCore.GLOBAL_TIME

    #UNCOMMENT THIS IF YOU WANT TO CREATE SERIES OF PHOTOS/VIDEO AND MODIFY HOW MANY PICTURES SHOULD BE TAKEN
    #SAVE EVERY 20TH SECOND photos of the simulation
    if (time % 20 == 0):
        cv2.imwrite("saved_photos/" + str(time) + ".jpg", cv2_img)

    #SAVE the data about vehicles to csv at the end MORNING NOON AFTERNOON
    if time > AFTERNOON_BORDER:
        if not WAS_SAVED:
            print(VEHICLES_INFO)
            with open('morning_data.csv', mode='w', newline='') as morning_data_file:
                morning_data_file_writer = csv.writer(morning_data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                for data in VEHICLES_INFO[0]:
                    morning_data_file_writer.writerow([str(data[0]), str(data[1]), str(data[2]), str(data[3]), str(data[4])])

            with open('noon_data.csv', mode='w', newline='') as noon_data_file:
                noon_data_file_writer = csv.writer(noon_data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                for data in VEHICLES_INFO[1]:
                    noon_data_file_writer.writerow([str(data[0]), str(data[1]), str(data[2]), str(data[3]), str(data[4])])

            with open('afternoon_data.csv', mode='w', newline='') as afternoon_data_file:
                afternoon_data_file_writer = csv.writer(afternoon_data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                for data in VEHICLES_INFO[2]:
                    afternoon_data_file_writer.writerow([str(data[0]), str(data[1]), str(data[2]), str(data[3]), str(data[4])])

            WAS_SAVED = True



    k = cv2.waitKey(1)
    if k==27:    # Esc key to stop
        continue

    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()

