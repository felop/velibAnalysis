import urllib3, json, os, time, datetime, requests
from glob import glob

class Velib(object):
    def __init__(self, id, meta=None):
        self.data = None
        self.id = id
        self.time_stamp = 0
        self.time    = None
        self.utc_time = None
        self.time_since_last_update = 0

        if id != 0:
            self._id = id-1
            if meta:
                self._time_stamp = meta
            else:
                self._time_stamp = json.load(open(paths["data"]+f"log_{self._id}.json", "r"))["lastUpdatedOther"]
        else:
            self._time_stamp = 0

    def download_data(self, http):
        while self._time_stamp >= self.time_stamp:
            try:
                self.data = json.loads(http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json").data)
            except Exception as error:
                report_log(self.time_stamp,self._time_stamp,3,f"failed request : {error}",log_id=self.id)
                time.sleep(10)
            else:
                self.data = json.loads(http.request("GET", "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json").data)
                self.time_stamp = self.data["lastUpdatedOther"]
                self.time    = datetime.datetime.fromtime_stamp(self.time_stamp)
                self.utc_time = datetime.datetime.fromtime_stamp(int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds()))
                self.time_since_last_update = (self.utc_time-self.time).total_seconds()
            if self.time_since_last_update > 120.0:
                report_log(self.time_stamp,self._time_stamp,2,f"skip : {int(time_since_last_update/60)}",log_id=self.id)
                time.sleep(59)

def report_log(ifttt_key,current_log_time="",prev_log_time="",level=0,info="-",log_id=""):
    if level < 4:
        if level == 3:
            requests.post(f"https://maker.ifttt.com/trigger/error/with/key/{ifttt_key}", data={"value1":info})
        level = ["INFO", "WARNING", "ERROR", "CRITICAL"][level]
        current_log_date, prev_log_date, time_gap = "-", "-", "-"
        if isinstance(current_log_time, int) and current_log_time != 0:
            current_log_time = datetime.datetime.fromtime_stamp(current_log_time)
            current_log_date = current_log_time.strftime("%d/%m/%Y %H:%M:%S ")
        else:
            current_log_time = ""
        if isinstance(prev_log_time, int) and prev_log_time != 0:
            prev_log_time = datetime.datetime.fromtime_stamp(prev_log_time)
            prev_log_date = prev_log_time.strftime("%d/%m/%Y %H:%M:%S ")
        else:
            prev_log_time = ""
        if current_log_date != "-" and prev_log_date != "-":
            time_gap = (current_log_time-prev_log_time)

        log_content = f"[ {level} ] {log_id} {current_log_date}{current_log_time} ; {prev_log_date}{prev_log_time} ; {time_gap} ; {info} \n"
    else:
        if level==4:
            log_content = f"[ starting ] {datetime.datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S ')}{int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds())}\n";

    with open("temporaryStorageA.log", "a") as log_file_A, open("temporaryStorageB.log", "a") as log_file_B:
        log_file_A.write(log_content);log_file_B.write(log_content)

with open("serv_files.json", "r") as file:
    paths = json.load(file)
ifttt_key = open(paths["ifttt"], "r").read()
files = glob(paths["data"]+"*.json")
http = urllib3.PoolManager()

report_log(ifttt_key, level=4)
if len(files) == 0:
    log = Velib(0)
    log.download_data(http)
    with open(paths["data"]+"log_0.json", "w+") as file:
        json.dump(log.data, file)
    report_log(ifttt_key, log.time_stamp, log_id=0)
else:
    log = Velib(max([int(files[id].split("_")[1].split(".")[0]) for id in range(len(files))]))
    log.time_stamp = json.load(open(paths["data"]+"log_"+str(log.id)+".json", "r"))["lastUpdatedOther"]

while 1:
    prev_log = log
    log = Velib(prev_log.id+1, meta=prev_log.time_stamp)
    log.download_data(http)
    with open(f"{paths['data']}log_{log.id}.json", "w+") as file:
        json.dump(log.data, file)
    report_log(ifttt_key, log.time_stamp, log._time_stamp, log_id=log.id)
    time.sleep(59)