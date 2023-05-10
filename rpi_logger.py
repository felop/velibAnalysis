import time, datetime, scp, paramiko, os, json
from glob import glob

with open("rpi_credentials.json", "r") as file:
    sshCred = json.load(file)

ssh_client=paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=sshCred["hostname"],port=sshCred["port"],username=sshCred["username"],key_filename=sshCred["key_filename"], password=sshCred["password"])

def getInfos():
    stdin, stdout, stderr = ssh_client.exec_command('ls data | wc -l')
    serverNbFiles = int(stdout.readlines()[0].split("\n")[0])
    stdin, stdout, stderr = ssh_client.exec_command('du -sh data')
    datasetSize = int(stdout.readlines()[0].split("\t")[0])
    stdin, stdout, stderr = ssh_client.exec_command('ls data')
    fileIdsList = [int(file.split("_")[1].split(".")[0]) for file in stdout.readlines()]
    firstFile = min(fileIdsList)
    lastFile = max(fileIdsList)
    return serverNbFiles, datasetSize, fileIdsList, firstFile, lastFile

with open("rpi_files.json", "r") as file:
    paths = json.load(file)
iftttKey = open(paths["ifttt"], "r").read()
def getFiles():
    global ssh_client, paths
    stdin, stdout, stderr = ssh_client.exec_command('ls data')
    fileIds = [int(file.split(".json")[0].split("log_")[1]) for file in stdout.readlines()]
    ftp_client=ssh_client.open_sftp()
    for fileId in sorted(fileIds)[:-1]:
        file_name = "log_"+str(fileId)+".json"
        ftp_client.get(f"/home/user0/data/{file_name}", paths["buffer"]+file_name)
    ftp_client.get(paths["distantLoggingFile"], paths["distantLoggingFile_destinationA"])
    ftp_client.close()

    os.system(f'cp {paths["distantLoggingFile_destinationA"]} {paths["distantLoggingFile_destinationB"]}')

    bufferFiles = [int(file_name.split(".json")[0].split("log_")[1]) for file_name in glob(paths["buffer"]+"*.json")]
    if sorted(bufferFiles) == sorted(fileIds)[:-1]:
        reportLog(info=f"downloaded {len(bufferFiles)} logs ; first : {sorted(bufferFiles)[0]} ; last : {sorted(bufferFiles)[-1]}")
    else:
        reportLog(info=f"download failed ; started with {sorted(fileIds)[:-1]}, ended with {sorted(bufferFiles)}")

    for fileId in sorted(bufferFiles):
        file_name = "log_"+str(fileId)+".json"
        stdin, stdout, stderr = ssh_client.exec_command(f'echo {file_name}>>/home/user0/deletionQueue.txt')
        os.system(f'mv {paths["buffer"]+file_name} {paths["disk"]+file_name}')

def reportLog(level=0,info="-"):
    global paths
    date = datetime.datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')
    dateSeconds = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())
    if level < 4:
        if level == 3:
            requests.post(f"https://maker.ifttt.com/trigger/error/with/key/{iftttKey}", data={"value1":info})
        level = ["INFO", "WARNING", "ERROR", "CRITICAL"][level]
        logContent = f"[ {level} ] {date} {dateSeconds} ; {info} \n"
    else:
        if level==4:
            logContent = f"[ starting ] {date} {dateSeconds} \n"

    with open(paths["loggingFileA"], "a") as logFileA, open(paths["loggingFileB"], "a") as logFileB:
        logFileA.write(logContent);logFileB.write(logContent)

if len(glob(paths["disk"]+"*.json")) == 0:
    reportLog(4)

getFiles()
ssh_client.close()
