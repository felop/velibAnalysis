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
                self._timeStamp = meta
            else:
                self._timeStamp = json.load(open(paths["data"]+f"log_{self._id}.json", "r"))["lastUpdatedOther"]
        else:
            self._timeStamp = 0

    def downloadData(self, http):
        while self._timeStamp >= self.timeStamp:
            try:
                self.data = json.loads(http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json").data)
            except Exception as error:
                reportLog(self.timeStamp,self._timeStamp,3,f"failed request : {error}",logId=self.id)
                time.sleep(10)
            else:
                self.data = json.loads(http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json").data)
                self.timeStamp = self.data["lastUpdatedOther"]
                self.time    = datetime.datetime.fromtimestamp(self.timeStamp)
                self.utcTime = datetime.datetime.fromtimestamp(int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds()))
                self.timeSinceLastUpdate = (self.utcTime-self.time).total_seconds()
            if self.timeSinceLastUpdate > 120.0:
                reportLog(self.timeStamp,self._timeStamp,2,f"skip : {int(timeSinceLastUpdate/60)}",logId=self.id)
                time.sleep(59)

def reportLog(currentLogTime="",prevLogTime="",level=0,info="-",logId=""):
    if level < 4:
        if level == 3:
            requests.post(f"https://maker.ifttt.com/trigger/error/with/key/{iftttKey}", data={"value1":info})
        level = ["INFO", "WARNING", "ERROR", "CRITICAL"][level]
        currentLogDate, prevLogDate, timeGap = "-", "-", "-"
        if isinstance(currentLogTime, int) and currentLogTime != 0:
            currentLogTime = datetime.datetime.fromtimestamp(currentLogTime)
            currentLogDate = currentLogTime.strftime("%d/%m/%Y %H:%M:%S ")
        else:
            currentLogTime = ""
        if isinstance(prevLogTime, int) and prevLogTime != 0:
            prevLogTime = datetime.datetime.fromtimestamp(prevLogTime)
            prevLogDate = prevLogTime.strftime("%d/%m/%Y %H:%M:%S ")
        else:
            prevLogTime = ""
        if currentLogDate != "-" and prevLogDate != "-":
            timeGap = (currentLogTime-prevLogTime)

        logContent = f"[ {level} ] {logId} {currentLogDate}{currentLogTime} ; {prevLogDate}{prevLogTime} ; {timeGap} ; {info} \n"
    else:
        if level==4:
            logContent = f"[ starting ] {datetime.datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S ')}{int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds())}\n";

    with open("temporaryStorageA.log", "a") as logFileA, open("temporaryStorageB.log", "a") as logFileB:
        logFileA.write(logContent);logFileB.write(logContent)

with open("serv_files.json", "r") as file:
    paths = json.load(file)
iftttKey = open(paths["ifttt"], "r").read()
files = glob(paths["data"]+"*.json")
http = urllib3.PoolManager()

reportLog(level=4)
if len(files) == 0:
    log = Velib(0)
    log.downloadData(http)
    with open(paths["data"]+"log_0.json", "w+") as file:
        json.dump(log.data, file)
    reportLog(log.timeStamp, logId=0)
else:
    log = Velib(max([int(files[id].split("_")[1].split(".")[0]) for id in range(len(files))]))
    log.timeStamp = json.load(open(paths["data"]+"log_"+str(log.id)+".json", "r"))["lastUpdatedOther"]

while 1:
    prevLog = log
    log = Velib(prevLog.id+1, meta=prevLog.timeStamp)
    log.downloadData(http)
    with open(f"{paths['data']}log_{log.id}.json", "w+") as file:
        json.dump(log.data, file)
    reportLog(log.timeStamp, log._timeStamp, logId=log.id)
    time.sleep(59)
