import os

from dotenv import load_dotenv


class Credentials:
    def __init__(self):
        load_dotenv()
        self.sftp_hostname = os.getenv("SFTP_HOSTNAME")
        self.sftp_username = os.getenv("SFTP_USERNAME")
        self.sftp_password = os.getenv("SFTP_PASSWORD")
