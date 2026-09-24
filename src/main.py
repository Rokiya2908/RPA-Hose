import sys
import argparse
from pathlib import Path
import os
from sftpManipulation import *
from localManipulation import *

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

    args = parser.parse_args()

    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Download From: {args.downloadfrom}")

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

    #Creating folder
    create_folder(log_location)
    write_log(log_file_location,f"Create folder : {log_location}")
    create_folder(local_output_location)
    write_log(log_file_location,f"Create folder : {local_input_location}")
    create_folder(local_input_location)
    write_log(log_file_location,f"Create folder : {local_output_location}")
    
    #Checking the parameter
    input_location = str(args.input)
    output_location = str(args.output)
    download_option = str(args.downloadfrom).strip().lower()
    write_log(log_file_location,
              f"Starting download from : {download_option} from {input_location} then upload result to {output_location}")
    file_copied = []

    if(download_option == "sftp"):
        file_copied = copy_file_from_local_to_sftp(config_data["SFTPHost"],
                                     config_data["username"],
                                     config_data["password"],
                                     local_input_location,
                                     input_location,log_file_location)
        write_log(log_file_location,
            f"Total number of file has been copied from {input_location} is {len(file_copied)}")
        copy_file_from_local_to_sftp(config_data["SFTPHost"],
                                     config_data["username"],
                                     config_data["password"],
                                     local_output_location,
                                     output_location
                                     ,log_file_location)
    elif(download_option == "local"):
        file_copied = copy_file_from_local_to_local(input_location,local_input_location,log_file_location)
        write_log(log_file_location,
            f"Total number of file has been copied from {input_location} is {len(file_copied)}")
        copy_result_file_from_local(local_output_location,output_location,log_file_location)




if __name__ == "__main__":
    main()
