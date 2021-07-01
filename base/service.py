import logging
import os

import config
from base.managers import DB, SettingsManager
from base.data_classes import Settings


class IntegrityChecker:
    """
    This method performs a check whether a required program files exist and repair them if not.
    """
    logger = logging.getLogger(config.INT_CHECKER_LOGGER_NAME)
    log_file = logging.FileHandler(config.MAIN_LOG_PATH)
    error_stream = logging.StreamHandler()

    log_file.setLevel(logging.INFO)
    log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

    error_stream.setLevel(logging.WARNING)
    error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

    logger.addHandler(log_file)
    logger.addHandler(error_stream)
    logger.setLevel(logging.DEBUG)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IntegrityChecker, cls).__new__(cls)

        return cls.instance

    def check_db_existence(self):
        db_manager = DB()

        if not os.path.exists(config.DATABASE_FULL_PATH):
            self.logger.info('Database does not exist. Creating one...')
            try:
                os.makedirs(config.DATABASE_PATH)
            except FileExistsError:
                self.logger.info('Data folder exist, but database does not.')
            db_manager.create_default_structure()
            self.logger.info('Database file with default structure created successfully.')

    def check_settings_existence(self):
        self.logger.info('Checking for settings existence.')

        if not os.path.exists(config.SETTINGS_FULL_PATH):
            self.logger.info('Settings file does not exist. Creating with default settings...')
            settings_manager = SettingsManager()
            settings_manager.write_settings(Settings())
            settings_manager.make_startup_shortcut()

    def check(self):
        """
        Performs a main check and repairment.
        """

        # do not change an order of method calls. They are dependent on each other.
        self.check_db_existence()
        self.check_settings_existence()

