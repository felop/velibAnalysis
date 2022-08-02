import time
time.sleep(30)

import urllib3, json, os, time, datetime
from glob import glob

def getDataApi(lastLogId, logId):
    while lastLogId >= logId:
        data = http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json")
        data = json.loads(data.data)
        logId = data["lastUpdatedOther"]
        timeSinceLastUpdate = datetime.datetime.fromtimestamp(int(time.time())-logId).strftime('%H:%M:%S')
        print("failing "+str(int(time.time()))+" "+timeSinceLastUpdate,end='\r')
    return data,logId

http = urllib3.PoolManager()
path = "data/"

files = glob(path+"*")
if len(files) == 0:
    data,logId = getDataApi(0,0)
    with open(path+"log_0.json", "w+") as file:
        json.dump(data, file)
    files = glob(path+"*")
    lastLogNumber = 0
    lastLogId = logId
else:
    lastLogNumber = max([int(files[id].split("_")[1].split(".")[0]) for id in range(len(files))])
    lastLogId = json.load(open(path+"log_"+str(lastLogNumber)+".json", "r"))["lastUpdatedOther"]
    logId = lastLogId

while 1:
    data,logId = getDataApi(lastLogId, logId)
    with open(path+"log_"+str(lastLogNumber+1)+".json", "w+") as file:
        json.dump(data, file)
    print("log_"+str(lastLogNumber)+" = "+str(logId))
    lastLogNumber+=1
    lastLogId = logId
    time.sleep(60)
