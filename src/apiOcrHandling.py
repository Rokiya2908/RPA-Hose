import requests
from common import *
import json

def call_orc_for_extraction(api_key,api_url,file_location):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    with open(file_location, "rb") as file:
        files = {
            "file": file
        }

        response = requests.post(
            api_url,
            headers=headers,
            files=files
        )

    return {response.status_code,response.json()}

def process_extraction(api_key,api_url,list_of_files,log_location):
    write_log(log_location,f"Start to call api to extract the data")
    file_result = []
    for file in list_of_files:
        information = {}
        write_log(log_location,f"Start with this file {file}")
        code,response = call_orc_for_extraction(api_key,api_url,file)
        write_log(log_location,f"Call the api with status {code}")
        if(code == 200):
            result = json.dump(response)
            write_log(log_location,f"Data extraction successfully this is the result : {result}")
            information.update(response)
            information["Status"] = "Success"
            information["FileLocation"] = file
            file_result.append(information)
        else:
            write_log(log_location,f"Data extraction failed this is the result")
            information["Status"] = "Failed"
            information["FileLocation"] = file
            file_result.append(information)
    return file_result

def extraction_result_handling(api_key,api_url,list_of_files,excel_location,log_location):
    file_result = process_extraction(api_key,api_url,list_of_files,log_location)
    for item in file_result:
        if(item["Status"] == "Success"):
            # Call the excel manipulation here
            # Well many shit
            print("check")
    return None
