import json
from datetime import datetime

default_data = [0,[{'mechanical':0},{'ebike':0}],0,1,0,0]
stations_infos = lambda stations_infos : {station["station_id"]:[station["numBikesAvailable"],station["num_bikes_available_types"],station["numDocksAvailable"],station["is_installed"],station["is_returning"],station["is_renting"]] for station in stations_infos["data"]["stations"]}
stations_list = json.load(open("stations_list.json", "r"))

def get_log_data(logId, log_path : str):
    log_path = log_path+"log_"+str(logId)+".json"
    log_data = json.load(open(log_path, "r"))
    log_time_stamp = log_data["lastUpdatedOther"]
    log_data = stations_infos(log_data)
    return log_data,log_time_stamp

def epoch_to_date(epochTime,year=0,month=0,weekday=0,day=1,hour=1,minute=1,second=0):
    format_string = ":".join(list(filter(len,['%Y'*year,'%m'*month,'%w'*weekday,'%d'*day,'%H'*hour,'%M'*minute,'%S'*second])))
    return datetime.fromtimestamp(epochTime).strftime(format_string)

def sort_select(log_data):
    global stations_list, default_data
    new_log, fails = {}, []
    for station in stations_list:
        if station in log_data:
            new_log[station] = log_data[station]
        else:
            fails.append(station)
            new_log[station] = default_data
    return new_log

def data_to_ml_array(raw_data):
    log_data = {}
    station_id = 0
    for station in raw_data:
        if raw_data[station][2] != 0:
            log_data[station_id] = round(raw_data[station][0]/(raw_data[station][0]+raw_data[station][2]), 2)
        else:
            log_data[station_id] = 0
        station_id += 1
    return log_data
