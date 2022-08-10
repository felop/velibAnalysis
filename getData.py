import urllib3, json, os, time, datetime, requests
from glob import glob

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

http = urllib3.PoolManager()
path = "data/"
iftttKey = open("iftttKey.txt", "r").read()
files = glob(path+"*")
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
