from glob import glob
import sys, random, json

sys.path.append("../")
#from velibAPI import getLogData, EpochToDate, dataToMlArray, sortSelect

x_train = []
x_test = []
meta_train = []
meta_test = []
y_train = []
y_test = []
offset, batchSize = 1, 10

def appendBatchToJson(batch, path):
    for data in batch:
        with open(path, "a+") as file:
            file.seek(0,2)
            if file.tell() == 0:
                file.write("[")
                file.write(data)
            else:
                file.seek(-1,2)
                file.truncate()
                file.write(" ,")
                file.write(data)
            file.write("]")

def processLogs(process=0, offset=1, batchSize=1, nblogs=40000, logSavingBatch=1000):
    global x_train, meta_train, y_train
    folderPath = "off"+str(offset)+"_batch"+str(batchSize)

    if process == 1:
        logs = glob("../data/logs/*")
        for logId in tqdm(range(len(logs)-offset-batchSize)[:40000]):
            for batchRank in range(batchSize):
                batch = []
                rawData, timeStamp = getLogData(logId+batchRank,"../data/logs/")
                logData = dataToMlArray(sortSelect(rawData))
                logData = [logData[station] for station in logData]
                batch.append(logData)
            x_train.append(batch)
            date = EpochToDate(timeStamp,weekday=1,day=0).split(":")
            weekday, hour, minutes = round(int(date[0])/7, 3), round(int(date[1])/24, 3), round(int(date[2])/60, 3)
            meta_train.append([weekday,hour,minutes])

            logData = dataToMlArray(sortSelect(getLogData(logId+offset,"../data/logs/")[0]))
            logData = [logData[station] for station in logData]
            y_train.append([logData])

            if logId%logSavingBatch == 0:
                with open("preprocessedData/tempFileX.txt", "a") as tempFileX:
                    for i in range(logSavingBatch):
                        json.dump(x_train[i], tempFileX)
                    x_train = []
                with open("preprocessedData/tempFileY.txt", "a") as tempFileY:
                    for i in range(logSavingBatch):
                        json.dump(y_train[i], tempFileY)
                    y_train = []
                with open("preprocessedData/tempFileX2.txt", "a") as tempFileX2:
                    for i in range(logSavingBatch):
                        json.dump(meta_train[i], tempFileX2)
                    meta_train = []

        with open("preprocessedData/"+folderPath+"/x_train.json", "w") as file:
            json.dump(x_train, file)
        with open("preprocessedData/"+folderPath+"/y_train.json", "w") as file:
            json.dump(y_train, file)
        with open("preprocessedData/"+folderPath+"/meta_train.json", "w") as file:
                json.dump(meta_train, file)
    elif process == 0:
        x_train = json.load(open("preprocessedData/"+folderPath+"/x_train.json", "r"))
        y_train = json.load(open("preprocessedData/"+folderPath+"/y_train.json", "r"))
        meta_train = json.load(open("preprocessedData/"+folderPath+"/meta_train.json", "r"))

#processLogs(process=0, save=0, offset=1, batchSize=1)
