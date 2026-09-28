import os
import shutil
import time
import ntpath
import smbclient

from common import *

def has_credential(username,password):
    return (username and password
            and str(username).strip().upper() != "N/A"
            and str(password).strip().upper() != "N/A")


def get_server_from_unc_path(unc_path):
    # \\server\share\folder -> server
    normalized_path = str(unc_path).replace("/","\\").lstrip("\\")
    return normalized_path.split("\\")[0]


def build_unc_path(host,share_folder_path):
    # (192.168.1.10, RPA\input) -> \\192.168.1.10\RPA\input
    normalized_path = str(share_folder_path).replace("/","\\")
    if(normalized_path.startswith("\\\\")):
        return normalized_path
    return "\\\\" + str(host).strip("\\") + "\\" + normalized_path.lstrip("\\")


def connect_to_share_folder(host,port,username,password,log_location):
    share_connected = False
    retry_connection_count = 0
    while(not share_connected and retry_connection_count < 5):
        try:
            smbclient.register_session(host,username=username,password=password,port=port)
            write_log(log_location,f"Share folder connection established {host}:{port},{username}")
            share_connected = True
        except Exception as e:
            write_log(log_location,f"Error connecting to share folder: {e}")
            write_log(log_location,f"Error while establish the share folder connection with following details: {host}:{port},{username}")
            time.sleep(3)
            retry_connection_count += 1
    return share_connected


def copy_file_from_share_folder_to_local(host,port,username,password,share_folder_path,local_path,log_location):
    if(not host):
        host = get_server_from_unc_path(share_folder_path)
    share_folder_path = build_unc_path(host,share_folder_path)
    write_log(log_location,f"Copy file from share folder {share_folder_path} to {local_path}")
    files_downloaded = []

    # No credential -> use the Windows account running the bot to access the UNC path directly
    if(not has_credential(username,password)):
        write_log(log_location,f"No share folder credential, access {share_folder_path} with current Windows account")
        if(not os.path.exists(share_folder_path)):
            write_log(log_location,f"Share folder location not found or no permission : {share_folder_path}")
            return files_downloaded
        for item in os.listdir(share_folder_path):
            file_details = {}
            item_location = os.path.join(share_folder_path,item)
            if(os.path.isfile(item_location) and item.lower().endswith(".pdf")):
                item_local_path = os.path.join(local_path,item)
                try:
                    shutil.copy(item_location,item_local_path)
                    time.sleep(1)
                    write_log(log_location,f"Downloaded: {item}")
                    file_details = {
                        "originalPath" : item_location,
                        "localPath" : item_local_path
                    }

                    files_downloaded.append(file_details)
                except Exception as e:
                    write_log(log_location,f"Failed to download: {item} due to : {e}")
        return files_downloaded

    connection_alive = connect_to_share_folder(host,port,username,password,log_location)
    if(connection_alive):
        try:
            all_item = [item for item in smbclient.scandir(share_folder_path)
                        if item.is_file() and item.name.lower().endswith(".pdf")]
        except Exception as e:
            write_log(log_location,f"Unable to list share folder {share_folder_path} due to : {e}")
            smbclient.delete_session(host,port=port)
            return files_downloaded

        #Incase there aren't any files to download
        if(len(all_item) == 0):
            write_log(log_location,f"No file to download at share folder location : {share_folder_path}")

        #Start checking and downloading the files to local
        for item in all_item:
            file_details = {}
            item_location = ntpath.join(share_folder_path,item.name)
            item_local_path = os.path.join(local_path,item.name)
            try:
                write_log(log_location,f"Downloading: {item_location} to {item_local_path}")
                with smbclient.open_file(item_location,mode="rb") as remote_file:
                    with open(item_local_path,"wb") as local_file:
                        shutil.copyfileobj(remote_file,local_file)
                time.sleep(1)
                if(os.path.exists(item_local_path)):
                    write_log(log_location,f"Downloaded: {item.name}")
                    file_details = {
                        "originalPath" : item_location,
                        "localPath" : item_local_path,
                        "fileName" : item.name
                    }

                    files_downloaded.append(file_details)
                else:
                    write_log(log_location,f"Failed to download: {item.name}")
            except Exception as e:
                write_log(log_location,f"Failed to download: {item.name} due to : {e}")

        smbclient.delete_session(host,port=port)
    return files_downloaded


def move_file_to_completed(host,port,username,password,share_folder_path,file_downloaded,log_location):
    if not host:
        host = get_server_from_unc_path(share_folder_path)

    share_folder_path = build_unc_path(host, share_folder_path)
    completed_folder = ntpath.join(share_folder_path,"Completed",get_current_time_date())

    # No credential -> use current Windows account
    if not has_credential(username, password):
        for file in file_downloaded:
            try:
                source_file = file.get("originalPath")
                destination_file = ntpath.join(completed_folder,file.get("fileName"))
                write_log(log_location,f"Moving processed file {source_file} to {destination_file}")
                # Create Completed folder if it doesn't exist
                if not os.path.exists(completed_folder):
                    os.makedirs(completed_folder, exist_ok=True)
                    write_log(log_location,f"Created completed folder: {completed_folder}")
                if not os.path.isfile(source_file):
                    write_log(log_location,f"Source file not found: {source_file}")
                    continue
                shutil.move(source_file,destination_file)
                write_log(log_location,f"Moved successfully: from {source_file} to {destination_file}")
                continue
            except Exception as e:
                write_log(log_location,f"Failed to move {source_file}: {e}")
                return False


    write_log(log_location,f"Connect to Shared Newort folder with IP")
    # Credential-based SMB connection
    connection_alive = connect_to_share_folder(host,port,username,password,log_location)
    if not connection_alive:
        return False
    
        # Create Completed folder if it doesn't exist
    if not smbclient.path.exists(completed_folder):
        smbclient.mkdir(completed_folder)
        write_log(log_location,f"Created completed folder: {completed_folder}")
    for file in file_downloaded:
        try:
            source_file = file.get("originalPath")
            destination_file = ntpath.join(completed_folder,file.get("fileName"))
            # Check source file
            if not smbclient.path.isfile(source_file):
                write_log(log_location,f"Source file not found: {source_file}")
                continue
            # Move file
            smbclient.rename(source_file,destination_file)
            write_log(log_location,f"Moved successfully: from {source_file} to {destination_file}")
            continue
        except Exception as e:
            write_log(log_location,f"Failed to move {source_file}: {e}")
        finally:
            smbclient.delete_session(host,port=port)