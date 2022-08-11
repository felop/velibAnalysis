import urllib3, json, os, time, datetime, requests
from glob import glob

class Velib(object):
    def __init__(self, id, meta=None):
        self.data = None
        self.id = id
        self.timeStamp = 0
        self.time    = None
        self.utcTime = None
        self.timeSinceLastUpdate = 0

        if id != 0:
            self._id = id-1
            if meta:
                self._timeStamp = json.load(open(paths["data"]+f"log_{self._id}.json", "r"))["lastUpdatedOther"]
                self._time = datetime.datetime.fromtimestamp(self._timeStamp)
            else:
                self._timeStamp = meta[0]
                self._time = meta[1]

    def downloadData(self, http, lastLogTimeStamp):
        while lastLogTimeStamp >= logId:
            try:
                self.data = json.loads(http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json").data)
            except Exception as error:
                ##############
                reportLog(logId,lastLogTimeStamp,3,f"failed request : {error}",logNumber=lastLogNumber+1)
                ##############
                time.sleep(10)
            else:
                self.data = json.loads(http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json").data)
                self.timeStamp = self.data["lastUpdatedOther"]
                self.time    = datetime.datetime.fromtimestamp(self.timeStamp)
                self.utcTime = datetime.datetime.fromtimestamp(int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds()))
                self.timeSinceLastUpdate = (self.utcTime-self.time).total_seconds()
            if self.timeSinceLastUpdate > 120.0:
                ##############
                reportLog(logId,lastLogTimeStamp,2,f"skip : {int(timeSinceLastUpdate/60)}",logNumber=lastLogNumber+1)
                ##############
                time.sleep(59)

def reportLog(currentLog="",prevLog="",level=0,info="-",logNumber=""):
    if level < 4:
        if level == 3:
            requests.post(f"https://maker.ifttt.com/trigger/error/with/key/{iftttKey}", data={"value1":info})
        level = ["INFO", "WARNING", "ERROR", "CRITICAL"][level]
        currentDate, prevDate, timeGap = "-", "-", "-"
        if isinstance(currentLog, int) and currentLog != 0:
            currentTime = datetime.datetime.fromtimestamp(currentLog)
            currentDate = currentTime.strftime("%d/%m/%Y %H:%M:%S ")
        else:
            currentLog = ""
        if isinstance(prevLog, int) and prevLog != 0:
            prevTime = datetime.datetime.fromtimestamp(prevLog)
            prevDate = prevTime.strftime("%d/%m/%Y %H:%M:%S ")
        else:
            prevLog = ""
        if currentDate != "-" and prevDate != "-":
            timeGap = (currentTime-prevTime)

        log = f"[ {level} ] {logNumber} {currentDate}{currentLog} ; {prevDate}{prevLog} ; {timeGap} ; {info} \n"
    else:
        if level==4:
            log=f"[ starting ] {datetime.datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S ')}{datetime.datetime.fromtimestamp(int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds()))}\n";

    with open("temporaryStorageA.log", "a") as logFileA, open("temporaryStorageB.log", "a") as logFileB:
        logFileA.write(log);logFileB.write(log)

def getDataApi(lastLogId, logId, lastLogNumber):
    while lastLogId >= logId:
        try:
            data = http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json")
            data = json.loads(data.data)
        except Exception as error:
            reportLog(logId,lastLogId,3,f"failed request : {error}",logNumber=lastLogNumber+1)
            time.sleep(10)
        else:
            logId = data["lastUpdatedOther"]
            logTime = datetime.datetime.fromtimestamp(logId)
            utcTime = datetime.datetime.fromtimestamp(int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds()))
            timeSinceLastUpdate = (utcTime-logTime).total_seconds()
            if timeSinceLastUpdate > 120.0:
                reportLog(logId,lastLogId,2,f"skip : {int(timeSinceLastUpdate/60)}",logNumber=lastLogNumber+1)
                time.sleep(59)
    return data,logId

paths = {"data":"/home/user0/data/", "ifttt":"/root/iftttKey.txt", "loggingFileA":"/home/user0/temporaryStorageA.log", "loggingFileB":"/root/temporaryStorageB.log"}
iftttKey = open(paths["ifttt"], "r").read()
files = glob(path+"*")
http = urllib3.PoolManager()

if len(files) == 0:
    lastLogNumber = -1
    data,logId = getDataApi(0,0,lastLogNumber)
    with open(path+"log_0.json", "w+") as file:
        json.dump(data, file)
    reportLog(logId, logNumber=0)
    files = glob(path+"*")
    lastLogId = logId
else:
    lastLogNumber = max([int(files[id].split("_")[1].split(".")[0]) for id in range(len(files))])
    lastLogId = json.load(open(path+"log_"+str(lastLogNumber)+".json", "r"))["lastUpdatedOther"]
    logId = lastLogId

while 1:
    data,logId = getDataApi(lastLogId, logId)
    with open(path+"log_"+str(lastLogNumber+1)+".json", "w+") as file:
        json.dump(data, file)
    reportLog(logId,lastLogId,logNumber=lastLogNumber+1)
    lastLogNumber+=1
    lastLogId = logId
    time.sleep(59)
