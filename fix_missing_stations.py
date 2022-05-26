from glob import glob
from velibAPI import getLogData, EpochToDate, dataToMlArray
import json, urllib3

stationsInfos = lambda StationsInfos : {station["station_id"]:[station["numBikesAvailable"],station["num_bikes_available_types"],station["numDocksAvailable"],station["is_installed"],station["is_returning"],station["is_renting"]] for station in StationsInfos["data"]["stations"]}

defaultData = [0,{'mechanical':0},{'ebike':0},0,1,0,0]

stationsList = json.load(open("stationsList.json", "r"))

def fixMissingStations(logData):
    global stationsList, defaultData
    newLog, fails = {}, []
    for station in stationsList:
        if station in logData:
            newLog[station] = logData[station]
            fail = False
        else:
            fails.append(station)
            newLog[station] = defaultData
            fail = True
    return newLog, fail
