
import os
import json
import mimetypes
import requests
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

def upload_file_to_server(api_url,token,file_location,log_location,file_key="file",timeout=300):
    # POST multipart/form-data with Bearer token, return (status_code, response_data)
    write_log(log_location,f"Upload file {file_location} to {api_url}")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        with open(file_location, "rb") as file:
            files = {
                file_key: (os.path.basename(file_location), file,
                           mimetypes.guess_type(file_location)[0] or "application/octet-stream")
            }
            response = requests.post(
                api_url,
                headers=headers,
                files=files,
                timeout=timeout
            )
    except Exception as e:
        write_log(log_location,f"Unable to upload file {file_location} due to : {e}")
        return None,{}

    write_log(log_location,f"Upload file {file_location} with status {response.status_code}")
    if(response.status_code == 401):
        write_log(log_location,f"Token is invalid or expired, please update token in config")
    try:
        response_data = response.json()
    except ValueError:
        response_data = {"RawResponse": response.text}
    return response.status_code,response_data