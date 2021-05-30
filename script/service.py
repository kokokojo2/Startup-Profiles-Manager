import logging
import os

import config
from db.db_manager import DB


class IntegrityChecker:
    """
    This method performs a check whether a required program files exist and repair them if not.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IntegrityChecker, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(config.INT_CHECKER_LOGGER_NAME)
        log_file = logging.FileHandler(config.MAIN_LOG_PATH)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def check_db_existence(self):
        db_manager = DB()

        if not os.path.exists(config.DATABASE_FULL_PATH):
            self.logger.info('Database does not exist. Creating one...')
            os.makedirs(config.DATABASE_PATH)
            db_manager.create_default_structure()
            self.logger.info('Database file with default structure created successfully.')

    def check(self):
        """
        Performs a main check and repairment.
        """

        self.check_db_existence()

