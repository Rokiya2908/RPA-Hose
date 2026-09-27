import os
from common import *
import json

def process_extraction(token,api_url,list_of_files,log_location,result_location=None):
    write_log(log_location,f"Start to call api to extract the data")
    file_result = []
    for file in list_of_files:
        information = {}
        write_log(log_location,f"Start with this file {file}")
        code,response = upload_file_to_server(api_url,token,file,log_location)
        result = json.dumps(response,ensure_ascii=False)
        if(code == 200):
            write_log(log_location,f"Data extraction successfully this is the result : {result}")
            if(result_location):
                result_file_location = os.path.join(result_location,os.path.splitext(os.path.basename(file))[0] + ".json")
                with open(result_file_location,"w",encoding="utf-8") as f:
                    json.dump(response,f,ensure_ascii=False,indent=2)
            if(isinstance(response,dict)):
                information.update(response)
            else:
                information["Data"] = response
            information["Status"] = "Success"
            information["FileLocation"] = file
            file_result.append(information)
        else:
            write_log(log_location,f"Data extraction failed this is the result : {result}")
            information["Status"] = "Failed"
            information["FileLocation"] = file
            file_result.append(information)
    return file_result

def extraction_result_handling(token,api_url,list_of_files,excel_location,log_location):
    file_result = process_extraction(token,api_url,list_of_files,log_location)
    for item in file_result:
        if(item["Status"] == "Success"):
            # Call the excel manipulation here
            # Well many shit
            print("check")
    return None
