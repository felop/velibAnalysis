import json
from datetime import datetime

#######################################
#### IMPORTANT :  BUILD ORDER FUNC ####
#######################################

defaultData = [0,[{'mechanical':0},{'ebike':0}],0,1,0,0]
stationsInfos = lambda StationsInfos : {station["station_id"]:[station["numBikesAvailable"],station["num_bikes_available_types"],station["numDocksAvailable"],station["is_installed"],station["is_returning"],station["is_renting"]] for station in StationsInfos["data"]["stations"]}
stationsList = json.load(open("stationsList.json", "r"))

def getLogData(logId, logPath : str):
    logPath = logPath+"log_"+str(logId)+".json"
    logData = json.load(open(logPath, "r"))
    logTimeStamp = logData["lastUpdatedOther"]
    logData = stationsInfos(logData)
    return logData,logTimeStamp

def EpochToDate(epochTime,year=0,month=0,weekday=0,day=1,hour=1,minute=1,second=0):
    formatString = ":".join(list(filter(len,['%Y'*year,'%m'*month,'%w'*weekday,'%d'*day,'%H'*hour,'%M'*minute,'%S'*second])))
    return datetime.fromtimestamp(epochTime).strftime(formatString)

def sortSelect(logData):
    global stationsList, defaultData
    newLog, fails = {}, []
    for station in stationsList:
        if station in logData:
            newLog[station] = logData[station]
        else:
            fails.append(station)
            newLog[station] = defaultData
    return newLog

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
