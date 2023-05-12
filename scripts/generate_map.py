import urllib3, json, time, datetime, cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage.filters import gaussian_filter
from tqdm import tqdm
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))
from velib_utils import get_log_data, epoch_to_date

def myplot(x, y, s, bins=1000):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap.T, extent

# GET ALL STATION'S GPS INFO
http = urllib3.PoolManager()
path = "data/stationsInfos/"

data = http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json")
data = json.loads(data.data)
with open(path+"station_information.json", "w+") as file:
    json.dump(data, file)

stations_data = data["data"]["stations"]
stations_data = {station["station_id"]:[station["lat"],station["lon"],station["capacity"]] for station in stations_data}
# GET ALL STATION'S GPS INFO

stations_data2 = {}

for station in stations_data:
    if stations_data[station][2] != 0 and stations_data[station][0] > 40 and stations_data[station][1] > 2:
        stations_data2[station] = [stations_data[station][0],stations_data[station][1],stations_data[station][2]]
stations_data = stations_data2
fig, ax = plt.subplots()
for i in tqdm(range(1)):  # 1640563200  1640649600
    log_data,time_stamp = get_log_data(i+207)

    x = [stations_data[station][1] for station in stations_data]
    y = [stations_data[station][0] for station in stations_data]
    c = [log_data[station][0] for station in stations_data]

    fig = plt.figure()
    img, extent = myplot(x, y, 15)
    plt.imshow(img, extent=extent, origin='lower', cmap=cm.jet)
    plt.show()

    #time_stamp = epoch_to_date(i)
    #ax.scatter(x, y, c=c,  cmap=plt.get_cmap('inferno'))
    #ax.imshow(mpimg.imread('paris.png'), extent=(2.211501, 2.469387, 48.803492, 48.915118))
    #plt.title(str(time_stamp),loc="center")
    #plt.savefig('heatMap_'+str(i))#'generatedMaps/nbVelos/'+str(i))
    #ax.cla()
#48.915118, 2.469387   48.914997, 2.469387
#48.803492, 2.211684   48.804938, 2.470120
