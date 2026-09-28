import os
import shutil
import time
from common import *

def copy_file_from_local_to_local(local_input_location,processing_location,log_location):
    write_log(log_location,f"Copy file from {local_input_location} to {processing_location}")
    file_copied = []
    if(os.path.exists(local_input_location)):
        file_details = {}
        for item in os.listdir(local_input_location):
            item_location = os.path.join(local_input_location,item)
            write_log(log_location,f"Current at file from {item}")
            write_log(log_location,f"Current at file from {item_location}")
            write_log(log_location,f"{os.path.isfile(item_location)}")
            if(os.path.isfile(item_location)):
                if(str(item).lower().endswith(".pdf")):
                    try:
                        processing_file_location = os.path.join(processing_location,item)
                        write_log(log_location,f"Copy file from {item_location} to {processing_file_location}")
                        shutil.copy(item_location,processing_file_location)
                        time.sleep(1)
                        file_details = {
                            "originalPath" : item_location,
                            "localPath" : processing_file_location,
                             "fileName" : item
                        }
                        file_copied.append(file_details)
                    except Exception as e:
                        write_log(log_location,f"Unable to file from {item_location} to {processing_file_location}")
    
    return file_copied

def copy_result_file_from_local(file_processed,output_location,log_location):
    write_log(log_location,f"Start move file to completed")
    final_location = os.path.join(output_location,"Completed",get_current_time_date())
    for file_details in file_processed:
        source_location = file_details.get("originalPath")
        write_log(log_location,f"Copy file from {source_location} to {final_location}")
        if(os.path.exists(final_location)== False):
            write_log(log_location,f"{final_location} doesn't exist create new")
            os.mkdir(final_location)
        
        try:
            file_completed_location = os.path.join(final_location,file_details.get("fileName"))
            write_log(log_location,f"Move file from {source_location} to  {file_completed_location}")   
            shutil.move(source_location,file_completed_location)
            
        except Exception as e:
            write_log(log_location,f"Can't copy the file to output folder due to {e}")   
            write_log(log_location,f"Please take the result file this location {source_location}")   
    