import numpy as np
from math import sqrt
import cv2
import random

def distance_map(xSize: int, ySize: int, data: list):   # data: [xPos, yPos, val]
    blank_map = np.zeros((ySize,xSize))
    data = np.array(data)
    data = np.float64(data)
    print(data[0])
    x_min, x_max = min([i[0] for i in data]), max([i[0] for i in data])
    y_min, y_max = min([i[1] for i in data]), max([i[1] for i in data])
    data_mapped = [ [(i[0]-x_min)/x_max*xSize, (i[1]-y_min)/y_max*ySize, 1] for i in data]
    for y_pixel in range(len(blank_map)):
        for x_pixel in range(len(blank_map[y_pixel])):
            blank_map[y_pixel, x_pixel] = min([sqrt(abs(point[0]-x_pixel)**2+abs(point[1]-y_pixel)**2) for point in data_mapped])
    return blank_map/blank_map.max()

def colorize(heat_map: list, color="redToBlue"):
    heat_map = np.float32(heat_map)
    heat_map = cv2.cvtColor(heat_map,cv2.COLOR_GRAY2RGB)
    for y_pixel in range(len(heat_map)):
        for x_pixel in range(len(heat_map[y_pixel])):
            if color == "redToBlue":
                bw_color = heat_map[y_pixel, x_pixel][0]
                heat_map[y_pixel, x_pixel] = np.array([bw_color,.3-bw_color,1-bw_color])
    return heat_map


if __name__ == "__main__":
    tab = [[random.random(), random.random()] for _ in range(random.randint(5,15))]

    heat_map = colorize(distance_map(100,100,tab))
    heat_map = cv2.resize(heat_map,(500,500))
    cv2.imshow("frame",heat_map)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
