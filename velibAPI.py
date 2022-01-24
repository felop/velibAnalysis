import json
from datetime import datetime

def getLogData(logId):
    logPath = "../data/logs/log_"+str(logId)+".json"
    logData = json.load(open(logPath, "r"))
    logTimeStamp = logData["lastUpdatedOther"]
    logData = {station["station_id"]:[station["numBikesAvailable"],station["num_bikes_available_types"],station["numDocksAvailable"],station["is_installed"],station["is_returning"],station["is_renting"]] for station in logData["data"]["stations"]}
    return logData,logTimeStamp

def EpochToDate(epochTime,year=0,month=0,weekday=0,day=1,hour=1,minute=1,second=0):
    formatString = ":".join(list(filter(len,['%Y'*year,'%m'*month,'%w'*weekday,'%d'*day,'%H'*hour,'%M'*minute,'%S'*second])))
    return datetime.fromtimestamp(epochTime).strftime(formatString)

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
