import os


class Credentials:
    def __init__(self):
        self.sftp_hostname = os.getenv("SFTP_HOSTNAME")
        self.sftp_username = os.getenv("SFTP_USERNAME")
        self.sftp_password = os.getenv("SFTP_PASSWORD")
