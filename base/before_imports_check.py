import os
import config


def check():
    check_root_folder_existence()
    check_log_folder_existence()


def check_log_folder_existence():
    if not os.path.exists(config.LOGS_DIR):
        os.makedirs(config.LOGS_DIR)


def check_root_folder_existence():
    if not os.path.exists(config.APPLICATION_ROOT):
        os.makedirs(config.APPLICATION_ROOT)
