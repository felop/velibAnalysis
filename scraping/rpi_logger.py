import requests, datetime, scp, paramiko, os, json
from glob import glob

def get_infos(ssh_client):
    stdin, stdout, stderr = ssh_client.exec_command('ls data | wc -l')
    server_nb_files = int(stdout.readlines()[0].split("\n")[0])
    stdin, stdout, stderr = ssh_client.exec_command('du -sh data')
    dataset_size = int(stdout.readlines()[0].split("\t")[0])
    stdin, stdout, stderr = ssh_client.exec_command('ls data')
    file_ids_list = [int(file.split("_")[1].split(".")[0]) for file in stdout.readlines()]
    first_file = min(file_ids_list)
    last_file = max(file_ids_list)
    return server_nb_files, dataset_size, file_ids_list, first_file, last_file

def get_files(ssh_client, paths):
    stdin, stdout, stderr = ssh_client.exec_command('ls data')
    file_ids = [int(file.split(".json")[0].split("log_")[1]) for file in stdout.readlines()]
    ftp_client=ssh_client.open_sftp()
    for file_id in sorted(file_ids)[:-1]:
        file_name = "log_"+str(file_id)+".json"
        ftp_client.get(f"/home/user0/data/{file_name}", paths["buffer"]+file_name)
    ftp_client.get(paths["distantLoggingFile"], paths["distantLoggingFile_destinationA"])
    ftp_client.close()

    os.system(f'cp {paths["distantLoggingFile_destinationA"]} {paths["distantLoggingFile_destinationB"]}')

    buffer_files = [int(file_name.split(".json")[0].split("log_")[1]) for file_name in glob(paths["buffer"]+"*.json")]
    if sorted(buffer_files) == sorted(file_ids)[:-1]:
        report_log(info=f"downloaded {len(buffer_files)} logs ; first : {sorted(buffer_files)[0]} ; last : {sorted(buffer_files)[-1]}")
    else:
        report_log(info=f"download failed ; started with {sorted(file_ids)[:-1]}, ended with {sorted(buffer_files)}")

    for file_id in sorted(buffer_files):
        file_name = "log_"+str(file_id)+".json"
        stdin, stdout, stderr = ssh_client.exec_command(f'echo {file_name}>>/home/user0/deletionQueue.txt')
        os.system(f'mv {paths["buffer"]+file_name} {paths["disk"]+file_name}')

def report_log(paths,level=0,info="-"):
    date = datetime.datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')
    date_seconds = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())
    if level < 4:
        if level == 3:
            requests.post(f"https://maker.ifttt.com/trigger/error/with/key/{ifttt_key}", data={"value1":info})
        level = ["INFO", "WARNING", "ERROR", "CRITICAL"][level]
        log_content = f"[ {level} ] {date} {date_seconds} ; {info} \n"
    else:
        if level==4:
            log_content = f"[ starting ] {date} {date_seconds} \n"

    with open(paths["loggingFileA"], "a") as log_file_A, open(paths["loggingFileB"], "a") as log_file_B:
        log_file_A.write(log_content);log_file_B.write(log_content)


with open("rpi_credentials.json", "r") as file:
    ssh_cred = json.load(file)
with open("rpi_files.json", "r") as file:
    paths = json.load(file)

ssh_client=paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=ssh_cred["hostname"],port=ssh_cred["port"],username=ssh_cred["username"],key_filename=ssh_cred["key_filename"], password=ssh_cred["password"])
ifttt_key = open(paths["ifttt"], "r").read()

if len(glob(paths["disk"]+"*.json")) == 0:
    report_log(paths,4)

get_files(ssh_client, paths)
ssh_client.close()
