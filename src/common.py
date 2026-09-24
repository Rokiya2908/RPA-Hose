
import os
import json
from datetime import datetime

def write_log(log_location,log_message):
    if(not os.path.exists(log_location)):
        with open(log_location, 'w',encoding="utf-8") as f:
            f.write(f"{get_current_time_date()}: {log_message}\n")
    else:
        with open(log_location, 'a',encoding="utf-8") as f:
            f.write(f"{get_current_time_date()}: {log_message}\n")

def read_configuration(configuration_location):
    with open(configuration_location,'r') as f:
        config = json.load(f)
        return config
    
def create_folder(folder_path):
    if(not os.path.exists(folder_path)):
        os.makedirs(folder_path)

def get_current_time_date():
    date_time = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
    return date_time