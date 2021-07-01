import os
import config


def check():
    check_log_folder_existence()


def check_log_folder_existence():
    if not os.path.exists(config.LOGS_DIR):
        os.makedirs(config.LOGS_DIR)
