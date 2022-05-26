import json, urllib3

http = urllib3.PoolManager()
fails = []

data = http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json")
data = json.loads(data.data)
stationsData = [station["station_id"] for station in data["data"]["stations"]]
with open("stationsList.json", "w+") as file:
    json.dump(stationsData, file)
