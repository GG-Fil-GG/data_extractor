import os
import shutil
import logging
import schedule
import time
from datetime import datetime, timedelta

def cleanup_old_files():
    temp_root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    now = datetime.now()
    age_threshold = timedelta(hours=24)

    if os.path.exists(temp_root_dir):
        for folder in os.listdir(temp_root_dir):
            folder_path = os.path.join(temp_root_dir, folder)
            if os.path.isdir(folder_path):
                folder_age = now - datetime.fromtimestamp(os.path.getctime(folder_path))
                if folder_age > age_threshold:
                    try:
                        shutil.rmtree(folder_path)
                        logging.info(f"Deleted old temp directory: {folder_path}")
                    except Exception as e:
                        logging.error(f"Error deleting {folder_path}: {e}")

def run_cleanup_job():
    schedule.every(1).hour.do(cleanup_old_files)

    while True:
        schedule.run_pending()
        time.sleep(1)