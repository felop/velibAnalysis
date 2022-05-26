import numpy as np
from math import sqrt
import cv2
import random

def distanceMap(xSize: int, ySize: int, data: list):   # data: [xPos, yPos, val]
    blankMap = np.zeros((ySize,xSize))
    data = np.array(data)
    data = np.float64(data)
    print(data[0])
    xMin, xMax = min([i[0] for i in data]), max([i[0] for i in data])
    yMin, yMax = min([i[1] for i in data]), max([i[1] for i in data])
    dataMapped = [ [(i[0]-xMin)/xMax*xSize, (i[1]-yMin)/yMax*ySize, 1] for i in data]
    for yPixel in range(len(blankMap)):
        for xPixel in range(len(blankMap[yPixel])):
            blankMap[yPixel, xPixel] = min([sqrt(abs(point[0]-xPixel)**2+abs(point[1]-yPixel)**2) for point in dataMapped])
    return blankMap/blankMap.max()

def colorize(heatMap: list, color="redToBlue"):
    heatMap = np.float32(heatMap)
    heatMap = cv2.cvtColor(heatMap,cv2.COLOR_GRAY2RGB)
    for yPixel in range(len(heatMap)):
        for xPixel in range(len(heatMap[yPixel])):
            if color == "redToBlue":
                bwColor = heatMap[yPixel, xPixel][0]
                heatMap[yPixel, xPixel] = np.array([bwColor,.3-bwColor,1-bwColor])
    return heatMap


if __name__ == "__main__":
    tab = [[random.random(), random.random()] for _ in range(random.randint(5,15))]

    heatMap = colorize(distanceMap(100,100,tab))
    heatMap = cv2.resize(heatMap,(500,500))
    cv2.imshow("frame",heatMap)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
