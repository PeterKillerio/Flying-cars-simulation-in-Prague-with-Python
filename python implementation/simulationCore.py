import csv
import math
from random import seed
from random import random
from random import randint

# time that represents 0 AM IS 0 AND AT *6 AM ITS 21,600
GLOBAL_TIME = 21600
GLOBAL_TIME_HOURS = str(int(21600/60/60))
GLOBAL_TIME_MINUTES = 0
# This is the equal change where the probability will be same across country/city *11 AM
GLOBAL_TIME_CHANGE_EQUAL = 39600
# This is the time where the probabilities reverse *3 PM
GLOBAL_TIME_CHANGE_REVERSE = 54000
# We will stop the simulation at *8 PM
GLOBAL_TIME_END_TIME = 72000

def tick_clock():
    global GLOBAL_TIME, GLOBAL_TIME_HOURS, GLOBAL_TIME_MINUTES
    GLOBAL_TIME_HOURS = str(int((GLOBAL_TIME/60)/60))
    GLOBAL_TIME_MINUTES = str(int((((GLOBAL_TIME/60)/60) - int((GLOBAL_TIME/60)/60))*60))

    if(GLOBAL_TIME % 60 == 0):

        print("TIME OF THE DAY IS: " + GLOBAL_TIME_HOURS + " HOURS and " + GLOBAL_TIME_MINUTES + " MINUTES")

    GLOBAL_TIME += 1

def load_boxes():
    BOXES = [[],[],[],[],[]]
    with open('boxes.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            BOXES[int(row[4])].append([[int(row[0]),int(row[1])],[int(row[2]), int(row[3])]])
            #print(f'x[0]: \t{row[0]} x[1]: {row[1]} y[0]: {row[2]} y[1]: {row[3]} order: {row[4]}.')
            line_count += 1
        print(f'Processed {line_count} lines.')

    return BOXES

def calculate_distance(pointA, pointB):

    A_squared = (pointA[0] - pointB[0])**2
    B_squared = (pointA[1] - pointB[1])**2
    return int(math.sqrt(A_squared + B_squared))

def pick_by_probability(outsider):
    #VERSION 2.0
    #This function also takes the time into the consideration, we will have 3 waves of changes
    # the first change will be the default, the time will begin at 6 AM and the probability will from
    # outside to inside, then at lets say 11pm the probability will flow equally across the country/city/
    # and then lets say at 3 pm the probability will flow from the inside out
    # THIS function has an argument outsider, so if the outsider is true that means we take the car from the outside as
    # the destination start.. WE WILL FAVOR HIM THE PROBABILITY FROM THE START ON THE COUNTRY EDGE
    # then it will be equal across and then we will reverse those
    # if the ousider is False then this car the final destination
    # time will start at 0AM and it will be 0 seconds


    # This function returns a value from 0-4 based on the written DENSITY OF POPULATION in designated area
    # This density is represented by an interval, lets say we have 2 areas and the first is 2x more
    # dense than the another, i.e A = 2.B, than there is 2x as bigger probability that we choose A over B,
    # we would pick random number from interval (1,4) but now we have 5 areas and probability interval looks as follows

    probability_interval = [1, 2.9, 7.7, 18.1, 45]
    probability_interval_reversed = [45, 18.1, 7.7, 2.9, 1]

    # These probabilities were calculated with help from the density heatmap legend, the area with the lowest density
    # was our baseline i.e 1 and the others were the multipliers of that baseline

    # random seed value
    seed()

    global GLOBAL_TIME, GLOBAL_TIME_CHANGE_EQUAL, GLOBAL_TIME_CHANGE_REVERSE, GLOBAL_TIME_END_TIME

    # I COULD MADE IT IN A FEWER LINES OF CODE BUT I WANTED IT CHRONOLOGICAL , FROM MORNING TO EVENING

    if GLOBAL_TIME < GLOBAL_TIME_CHANGE_EQUAL:
        if outsider:
            # generate random numbers between 0-46 which is the max from pr. interval
            value = (random() * probability_interval_reversed[0])

            for i in range(len(probability_interval_reversed)-1, -1, -1):
                if value < probability_interval_reversed[i]:
                    return i
        else:
            # generate random numbers between 0-46 which is the max from pr. interval
            value = (random() * probability_interval[-1])

            for i in range(len(probability_interval)):
                if value < probability_interval[i]:
                    return i
    elif GLOBAL_TIME < GLOBAL_TIME_CHANGE_REVERSE:
        # everybody is equally chosen
        value = randint(0, len(probability_interval)-1)
        return value

    elif GLOBAL_TIME < GLOBAL_TIME_END_TIME:
        # reversed the first one
        if not outsider:
            # generate random numbers between 0-46 which is the max from pr. interval
            value = (random() * probability_interval_reversed[0])

            for i in range(len(probability_interval_reversed) - 1, -1, -1):
                if value < probability_interval_reversed[i]:
                    return i
        else:
            # generate random numbers between 0-46 which is the max from pr. interval
            value = (random() * probability_interval[-1])

            for i in range(len(probability_interval)):
                if value < probability_interval[i]:
                    return i
    return -1




def pick_random_row(arr):
    seed()
    return randint(0, len(arr)-1)

def pick_start_end_point(boxes, min_distance):
    pointA = 0
    pointB = 0

    while True:
        orderA = pick_by_probability(True)
        orderB = pick_by_probability(False)

        if(orderA != -1 and orderB != -1):
            pointA = boxes[orderA][pick_random_row(boxes[orderA])]
            pointB = boxes[orderB][pick_random_row(boxes[orderB])]

            # middle of the box (pointA)
            A = [int((pointA[0][0] + pointA[1][0])/2),int((pointA[0][1] + pointA[1][1])/2)]
            # middle of the box (pointB)
            B = [int((pointB[0][0] + pointB[1][0])/2),int((pointB[0][1] + pointB[1][1])/2)]

            dist = calculate_distance(A, B)

            if dist > min_distance:
                break
        else:
            return -1


    return [A, B]

loaded_boxes = load_boxes()

# MINIMAL DISTANCE BETWEEN TWO PICKED POINTS IN PIXELS
# MINIMAL_DISTANCE = 150
# Print chosen start and end
#print(pick_start_end_point(loaded_boxes, MINIMAL_DISTANCE))

# print first box data
#print(loaded_boxes[0][0])

# print distance
#print(str(calculate_distance(loaded_boxes[0][0], loaded_boxes[3][50])))

# pick order
#pick_by_probability()
