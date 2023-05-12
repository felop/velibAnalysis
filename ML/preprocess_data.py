from glob import glob
import sys, random, json

x_train = []
x_test = []
meta_train = []
meta_test = []
y_train = []
y_test = []
offset, batch_size = 1, 10

def append_batch_to_json(batch, path):
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

def process_logs(process=0, offset=1, batch_size=1, nb_logs=40000, log_saving_batch=1000):
    global x_train, meta_train, y_train
    folder_path = "off"+str(offset)+"_batch"+str(batch_size)

    if process == 1:
        logs = glob("../data/logs/*")
        for log_id in tqdm(range(len(logs)-offset-batch_size)[:40000]):
            for batch_rank in range(batch_size):
                batch = []
                raw_data, time_stamp = getlog_data(log_id+batch_rank,"../data/logs/")
                log_data = data_to_ml_array(sort_select(raw_data))
                log_data = [log_data[station] for station in log_data]
                batch.append(log_data)
            x_train.append(batch)
            date = epoch_to_date(time_stamp,weekday=1,day=0).split(":")
            weekday, hour, minutes = round(int(date[0])/7, 3), round(int(date[1])/24, 3), round(int(date[2])/60, 3)
            meta_train.append([weekday,hour,minutes])

            log_data = dataToMlArray(sortSelect(getlog_data(log_id+offset,"../data/logs/")[0]))
            log_data = [log_data[station] for station in log_data]
            y_train.append([log_data])

            if log_id%log_saving_batch == 0:
                with open("preprocessedData/tempFileX.txt", "a") as tempFileX:
                    for i in range(log_saving_batch):
                        json.dump(x_train[i], tempFileX)
                    x_train = []
                with open("preprocessedData/tempFileY.txt", "a") as tempFileY:
                    for i in range(log_saving_batch):
                        json.dump(y_train[i], tempFileY)
                    y_train = []
                with open("preprocessedData/tempFileX2.txt", "a") as tempFileX2:
                    for i in range(log_saving_batch):
                        json.dump(meta_train[i], tempFileX2)
                    meta_train = []

        with open("preprocessedData/"+folder_path+"/x_train.json", "w") as file:
            json.dump(x_train, file)
        with open("preprocessedData/"+folder_path+"/y_train.json", "w") as file:
            json.dump(y_train, file)
        with open("preprocessedData/"+folder_path+"/meta_train.json", "w") as file:
                json.dump(meta_train, file)
    elif process == 0:
        x_train = json.load(open("preprocessedData/"+folder_path+"/x_train.json", "r"))
        y_train = json.load(open("preprocessedData/"+folder_path+"/y_train.json", "r"))
        meta_train = json.load(open("preprocessedData/"+folder_path+"/meta_train.json", "r"))

#process_logs(process=0, save=0, offset=1, batch_size=1)
