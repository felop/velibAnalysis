import keras, json, urllib3, time, math
from keras.models import load_model
import numpy as np
from datetime import datetime

#
stationsInfos = lambda StationsInfos : {station["station_id"]:[station["numBikesAvailable"],station["num_bikes_available_types"],station["numDocksAvailable"],station["is_installed"],station["is_returning"],station["is_renting"]] for station in StationsInfos["data"]["stations"]}
def dataToMlArray(rawData):
    logData = {}
    station_id = 0
    for station in rawData:
        if rawData[station][2] != 0:
            logData[station_id] = round(rawData[station][0]/(rawData[station][0]+rawData[station][2]), 2)
        else:
            logData[station_id] = 0
        station_id += 1
    return logData
#

http = urllib3.PoolManager()
data = http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json")
rawData = json.loads(data.data)

# META DATA
date = datetime.fromtimestamp(int(rawData["lastUpdatedOther"])).strftime('%w:%H:%M').split(":")
weekday, hour, minutes = round(int(date[0])/7, 3), round(int(date[1])/24, 3), round(int(date[2])/60, 3)
meta = [weekday,hour,minutes]
# META DATA

# VELIB DATA
data = stationsInfos(rawData)
MLdata = dataToMlArray(data)
MLdata = [MLdata[station] for station in MLdata]
# VELIB DATA

inputData = np.array([MLdata[:1436]])
inputMeta = np.array([meta])

model = load_model("netV2.h5")
prediction = model.predict({"input_1":inputData, "input_2":inputMeta})[0][0]*100

currentStats = [data[27033125][0], data[27033125][2]]
prediction = math.floor(prediction/100*(currentStats[0]+currentStats[1]))
prediction = [prediction, (currentStats[0]+currentStats[1])-prediction]
#
print(prediction,currentStats)
