import logging
import os
import win32com.client as win_client

import config


# a singleton class
class Validator:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Validator, cls).__new__(cls)

        return cls.instance

    def __init__(self):

        self.logger = logging.getLogger(config.VALIDATOR_LOGGER_NAME)
        log_file = logging.FileHandler(config.MAIN_LOG_PATH)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def bool_validate_name(self, name):
        if len(name) > 64:
            self.logger.warning(f'Name should be less then 64 characters, but input contains {len(name)} characters.')
            return False

        if len(name) == 0:
            self.logger.warning('Name should have at least one character.')
            return False

        return True

    def bool_validate_path(self, path):

        if not os.path.exists(path):
            self.logger.warning('Entered path does not exist.')
            return False

        if not path.endswith('.exe') and not path.endswith('.lnk'):
            self.logger.warning('Entered path does not refer to an exe file or shortcut.')
            return False

        return True

    def get_valid_priority(self, priority):

        try:
            priority = int(priority)
            return priority
        except ValueError:
            self.logger.warning('Priority should be a number.')

    def get_valid_path(self, path):

        if not self.bool_validate_path(path):
            return None

        if path.endswith('.exe'):
            return path

        if path.endswith('.lnk'):
            try:
                shell = win_client.Dispatch('WScript.Shell')
                link = shell.CreateShortCut(path)
                return link.Targetpath
            except Exception:
                self.logger.warning('Unknown error occur while trying to get target of a windows shortcut file. '
                                    'Please, enter a path to actual .exe file. Check properties of a shortcut to find '
                                    'it.')
                return None
