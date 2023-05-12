import cv2,os
from glob import glob
from tqdm import tqdm

img_array = []
images = sorted(glob('generatedMaps/TerminalOccupancies/*.png'), key=os.path.getmtime)

for filename in images:
    img = cv2.imread(filename)
    height, width, layers = img.shape
    size = (width,height)
    img_array.append(img)


out = cv2.VideoWriter('generatedMaps/TerminalOccupancies/video.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)

for i in tqdm(range(len(img_array))):
    out.write(img_array[i])
out.release()
