import urllib3, json, time, datetime, cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage.filters import gaussian_filter
from tqdm import tqdm
from velibAPI import getLogData, EpochToDate
import genHeatMap
import numpy as np

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

stationsData = data["data"]["stations"]
stationsData = {station["station_id"]:[station["lat"],station["lon"],station["capacity"]] for station in stationsData}
# GET ALL STATION'S GPS INFO

stationsData2 = {}

for station in stationsData:
    if stationsData[station][2] != 0 and stationsData[station][0] > 40 and stationsData[station][1] > 2:
        stationsData2[station] = [stationsData[station][0],stationsData[station][1],stationsData[station][2]]
stationsData = stationsData2
fig, ax = plt.subplots()
for i in tqdm(range(1)):  # 1640563200  1640649600
    logData,timeStamp = getLogData(i+207)

    x = [stationsData[station][1] for station in stationsData]
    y = [stationsData[station][0] for station in stationsData]
    c = [logData[station][0] for station in stationsData]

    fig = plt.figure()
    img, extent = myplot(x, y, 15)
    plt.imshow(img, extent=extent, origin='lower', cmap=cm.jet)
    plt.show()

    #timeStamp = EpochToDate(i)
    #ax.scatter(x, y, c=c,  cmap=plt.get_cmap('inferno'))
    #ax.imshow(mpimg.imread('paris.png'), extent=(2.211501, 2.469387, 48.803492, 48.915118))
    #plt.title(str(timeStamp),loc="center")
    #plt.savefig('heatMap_'+str(i))#'generatedMaps/nbVelos/'+str(i))
    #ax.cla()
#48.915118, 2.469387   48.914997, 2.469387
#48.803492, 2.211684   48.804938, 2.470120
