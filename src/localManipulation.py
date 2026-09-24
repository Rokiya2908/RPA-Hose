import os
import shutil
import time
from common import *

def copy_file_from_local_to_local(local_input_location,processing_location,log_location):
    write_log(log_location,f"Copy file from {local_input_location} to {processing_location}")
    file_copied = []
    if(os.path.exists(local_input_location)):
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
                        file_copied.append(processing_file_location)
                    except Exception as e:
                        write_log(log_location,f"Unable to file from {item_location} to {processing_file_location}")
    
    return file_copied

def copy_result_file_from_local(result_location,output_location,log_location):
    write_log(log_location,f"Copy file from {result_location} to {output_location}")
    copy_successfully = False
    if(os.path.exists(output_location)):
        try:
            shutil.copy(result_location,output_location)
            copy_successfully = True
        except Exception as e:
            write_log(log_location,f"Can't copy the file to output folder due to {e}")   
            write_log(log_location,f"Please take the result file this location {result_location}")   
    
    return copy_successfully