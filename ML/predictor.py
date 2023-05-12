import keras, json, urllib3, time, math
from keras.models import load_model
import numpy as np
from datetime import datetime

#
stations_infos = lambda stations_infos : {station["station_id"]:[station["numBikesAvailable"],station["num_bikes_available_types"],station["numDocksAvailable"],station["is_installed"],station["is_returning"],station["is_renting"]] for station in stations_infos["data"]["stations"]}
def data_to_ml_array(raw_data):
    log_data = {}
    station_id = 0
    for station in raw_data:
        if raw_data[station][2] != 0:
            log_data[station_id] = round(raw_data[station][0]/(raw_data[station][0]+raw_data[station][2]), 2)
        else:
            log_data[station_id] = 0
        station_id += 1
    return log_data
#

http = urllib3.PoolManager()
data = http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json")
raw_data = json.loads(data.data)

# META DATA
date = datetime.fromtimestamp(int(raw_data["lastUpdatedOther"])).strftime('%w:%H:%M').split(":")
weekday, hour, minutes = round(int(date[0])/7, 3), round(int(date[1])/24, 3), round(int(date[2])/60, 3)
meta = [weekday,hour,minutes]
# META DATA

# VELIB DATA
data = stations_infos(raw_data)
ML_data = data_to_ml_array(data)
ML_data = [ML_data[station] for station in ML_data]
# VELIB DATA

input_data = np.array([ML_data[:1436]])
input_meta = np.array([meta])

model = load_model("netV2.h5")
prediction = model.predict({"input_1":input_data, "input_2":input_meta})[0][0]*100

currentStats = [data[27033125][0], data[27033125][2]]
prediction = math.floor(prediction/100*(currentStats[0]+currentStats[1]))
prediction = [prediction, (currentStats[0]+currentStats[1])-prediction]
#
print(prediction,currentStats)
