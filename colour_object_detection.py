import cv2 as cv
import sys

def colour_filter(img, colour):
    """
    Returns a new image filtering every pixel (from the input image) that contains a colour other than the requested
    """
    
    # convert the image to HSV
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # dictionary containing the Hue values of each colour available
    colour_dic = {"red": [(0, 5), (170, 179)], "blue": [(105, 135)], "yellow": [(25, 35)], "green": [(45, 75)]}

    if colour not in colour_dic:
        sys.exit("colour not available")

    colour_selected = colour_dic[colour]

    mask = 0

    # threshold the HSV image according to the colour selected
    for colour_range in colour_selected:
        low_HSV = (colour_range[0] , 100, 100)
        high_HSV = (colour_range[1] , 255, 255)
        mask += cv.inRange(img_hsv, low_HSV, high_HSV)
        
    return mask
    

def largest_object(img):
    """
    Returns the polar coordinates (centre and radius) of the largest object found in the input image
    """

    # detect the edges of the image and find each contour 
    edges = cv.Canny(img, 150, 250)
    contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    contours_found = []

    if contours:

        # for each contour found, approximate the points of the contour to a circle and obtain its centre and radius 
        for _ , contour in enumerate(contours):
            #epsilon = 0.1*cv.arcLength(contour, True)
            contours_poly = cv.approxPolyDP(contour, 3, True)
            centre, radius = cv.minEnclosingCircle(contours_poly)
            centre = (round(centre[0],1), round(centre[1],1))
            contours_found.append((centre, radius))

        # select the biggest object based on the radius
        biggest_object = max(contours_found, key=lambda item:item[1])

        return biggest_object

    return (None, None)

