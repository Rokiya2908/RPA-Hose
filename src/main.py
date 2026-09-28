import sys
import argparse
from pathlib import Path
import os
from sftpManipulation import *
from localManipulation import *
from sharefolderManipulation import *
from apiOcrHandling import *

from common import *

# Add src to path
SRC_PATH = Path(__file__).parent
sys.path.insert(0, str(SRC_PATH))
PROJECT_PATH = SRC_PATH.parent
CONFIG_PATH = PROJECT_PATH / "config" / "config.json"

def main():
    print("Starting Bot...")
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--downloadfrom", required=True)
    # Remote machine information (SFTP / share folder), fallback to config if not provided
    parser.add_argument("--host", help="IP or hostname of the remote machine")
    parser.add_argument("--port", type=int, help="Default 22 for SFTP, 445 for share folder")
    parser.add_argument("--username", help="Account of the remote machine, domain account as DOMAIN\\user")
    parser.add_argument("--password", help="Password of the remote machine account")

    args = parser.parse_args()

    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Download From: {args.downloadfrom}")
    print(f"Host: {args.host}")

    config_data = None
    if(Path.exists(CONFIG_PATH)):    
        config_data = read_configuration(CONFIG_PATH)
    else:
        return None
    #init
    bot_location = os.path.join(config_data['BotFolderLocation'],get_current_time_date())
    log_location = os.path.join(bot_location,"logs")
    log_file_location = os.path.join(log_location,"log.txt")
    local_input_location = os.path.join(bot_location,"input")
    local_output_location = os.path.join(bot_location,"output")
    local_result_location = os.path.join(bot_location,"result")
    token = config_data.get("token")
    api_url = config_data.get("apiurl")

    #Creating folder
    create_folder(log_location)
    write_log(log_file_location,f"Create folder : {log_location}")
    create_folder(local_output_location)
    write_log(log_file_location,f"Create folder : {local_input_location}")
    create_folder(local_input_location)
    write_log(log_file_location,f"Create folder : {local_output_location}")
    create_folder(local_result_location)
    write_log(log_file_location,f"Create folder : {local_result_location}")
    
    #Checking the parameter
    input_location = str(args.input)
    output_location = str(args.output)
    download_option = str(args.downloadfrom).strip().lower()
    write_log(log_file_location,
              f"Starting download from : {download_option} from {input_location} then upload result to {output_location}")
    file_copied = []

    #Step 1 : download the files to local
    if(download_option == "sftp"):
        sftp_host = args.host or config_data.get("SFTPHost")
        sftp_port = args.port or 22
        sftp_username = args.username or config_data.get("username")
        sftp_password = args.password or config_data.get("password")
        write_log(log_file_location,f"Remote machine : {sftp_host}:{sftp_port},{sftp_username}")

        file_copied = copy_file_from_sftp_to_local(sftp_host,
                                     sftp_username,
                                     sftp_password,
                                     input_location,
                                     local_input_location,log_file_location,sftp_port)
        
    elif(download_option == "shared"):
        shared_host = args.host or config_data.get("SharedHost")
        if(str(shared_host).strip().upper() == "N/A"):
            shared_host = None
        shared_port = args.port or 445
        shared_username = args.username or config_data.get("SharedUsername")
        shared_password = args.password or config_data.get("SharedPassword")
        write_log(log_file_location,f"Remote machine : {shared_host}:{shared_port},{shared_username}")

        file_copied = copy_file_from_share_folder_to_local(shared_host,
                                     shared_port,
                                     shared_username,
                                     shared_password,
                                     input_location,
                                     local_input_location,log_file_location)
        if(shared_host):
            output_location = build_unc_path(shared_host,output_location)

    elif(download_option == "local"):
        file_copied = copy_file_from_local_to_local(input_location,local_input_location,log_file_location)
    else:
        write_log(log_file_location,f"Download option {download_option} is not supported, please use sftp / shared / local")
        return None
    write_log(log_file_location,
        f"Total number of file has been copied from {input_location} is {len(file_copied)}")

    #Step 2 : upload the files to the server to extract the data
    file_result = []
    if(len(file_copied) > 0):
        file_result = process_extraction(token,api_url,file_copied,log_file_location,local_result_location)
        total_success = len([item for item in file_result if item["Status"] == "Success"])
        write_log(log_file_location,
            f"Total number of file has been extracted successfully is {total_success}/{len(file_result)}")

    #Step 3 : upload the result to the output location
    if(download_option == "sftp"):
        copy_file_from_local_to_sftp(sftp_host,
                                     sftp_username,
                                     sftp_password,
                                     file_copied,
                                     output_location
                                     ,log_file_location,sftp_port)
    elif(download_option == "local"):
        copy_result_file_from_local(file_copied,output_location,log_file_location)
    elif(download_option == "shared"):
        move_file_to_completed(shared_host,
                               shared_port,
                               shared_username,
                               shared_password,
                               input_location,
                               file_copied,log_location)

    write_log(log_file_location,
            f"Bot finished processing for type {download_option}")

if __name__ == "__main__":
    main()
