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
            self.logger.warning(f'Name should be less then 64 characters long, but input contains {len(name)} characters.')
            return False, 'Name should be less then 64 characters long.'

        if len(name) == 0:
            self.logger.warning('Name should have at least one character.')
            return False, 'Name should have at least one character.'

        return True, name

    def bool_validate_path(self, path):
        self.logger.info(f'Trying to validate path "{path}"')

        if not os.path.exists(path):
            print(path)
            self.logger.warning('Entered path does not exist.')
            return False, 'Entered path does not exist.'

        if not path.endswith('.exe') and not path.endswith('.lnk'):
            self.logger.warning('Entered path does not refer to an exe file or shortcut.')
            return False, 'Entered path does not refer to an exe file or shortcut.'

        return True, path

    def get_valid_priority(self, priority):

        try:
            priority = int(priority)
            return True, priority
        except ValueError:
            self.logger.warning('Priority should be a number.')
            return False, 'Priority should be a number.'

    def get_valid_timeout(self, timeout):

        try:
            timeout = float(timeout)
            return True, timeout
        except ValueError:
            self.logger.warning('Timeout should be a number.')
            return False, 'Timeout should be a number.'

    def get_valid_path(self, path):

        if not self.bool_validate_path(path)[0]:
            return self.bool_validate_path(path)

        if path.endswith('.exe'):
            self.logger.info('Path validated successfully.')
            return True, path

        if path.endswith('.lnk'):
            self.logger.info('A shortcut has been detected.Trying to get target path...')

            try:
                shell = win_client.Dispatch('WScript.Shell')
                link = shell.CreateShortCut(path)
                self.logger.info('Target path captured. Validation completed.')

                return True, link.Targetpath
            except Exception:
                self.logger.warning('Unknown error occur while trying to get target of a windows shortcut file. '
                                    'Please, enter a path to actual .exe file. Check properties of a shortcut to find '
                                    'it.')
                return False, 'Unknown error occur while trying to get target of a windows shortcut file.'
