from pathlib import Path
from os import path
import paramiko
import time

from common import *

def connect_to_sftp(sftp_host,username,password,log_location):
    sftp_connected = False
    retry_connection_count = 0
    while(not sftp_connected and retry_connection_count < 5):
        try: 
            transport = paramiko.Transport((sftp_host, 22))
            transport.connect(username=username, password=password)
            if(transport.is_active):
                write_log(log_location,f"SFTP connection established {sftp_host},{username},{password}")
                sftp_connected = transport.is_active()
                return sftp_connected,transport
        except Exception as e:
            write_log(log_location,f"Error connecting to SFTP: {e}")
            write_log(log_location,f"Error while establish the SFTP connection with following details: {sftp_host},{username},{password}")
            time.sleep(3)
            retry_connection_count += 1
    return False,None

def copy_file_from_sftp_to_local(sftp_host,username,password,remote_path,local_path,log_location):
    connection_alive, transport = connect_to_sftp(sftp_host,username,password,log_location)
    files_downloaded = []
    if(connection_alive):
        sftp = paramiko.SFTPClient.from_transport(transport)
        all_item = sftp.listdir_attr(remote_path)

        #Incase there aren't any files to download
        if(len(all_item) == 0):
            write_log(log_location,f"No file to download at SFTP location : {remote_path}")
            transport.close()     
            return files_downloaded
        
        #Start checking and downloading the files to local
        for item in all_item:
            if(item.filename.endswith('.pdf')):
                try:
                    item_location = path.join(remote_path,item.filename)
                    item_local_path = path.join(local_path,item.filename)                
                    # Download
                    sftp.get(item_location, item_local_path)
                    write_log(log_location,f"Downloading: {item.location} to {item_local_path}")
                    time.sleep(1)
                    if(path.exists(item_local_path)):
                        write_log(log_location,f"Downloaded: {item.filename}")
                        files_downloaded.append(item_local_path)
                    else:
                        write_log(log_location,f"Failed to download: {item.filename}")
                except Exception as e:
                    write_log(log_location,f"Failed to download: {item.filename} due to : {e}")

        sftp.close()
        transport.close()
    return files_downloaded        

def copy_file_from_local_to_sftp(sftp_host,username,password,local_path,remote_path,log_location):
    connection_alive, transport = connect_to_sftp(sftp_host,username,password,log_location)
    upload_successfully = False
    if(connection_alive):
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path,remote_path)
        time.sleep(1)
        try:
            sftp.stat(remote_path)
            upload_successfully = True
        except Exception as e:
            write_log(log_location,f"Failed to upload: {local_path} due to : {e}")
            write_log(log_location,f"Please take the file from {local_path} to see the result")

    return upload_successfully        

        


    

    