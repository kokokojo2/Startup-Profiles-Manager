from subprocess import Popen
import logging

# logging constants
# TODO: should be moved to a global config file
logger_name = 'Startup scripts'
log_file_name = 'main_log.log'
log_file_format = '%(asctime)s - %(name)s:%(levelname)s: in %(funcName)s: %(message)s'
log_console_format = '%(asctime)s - %(name)s:%(levelname)s: %(message)s'


# a singleton class
class StartupManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StartupManager, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(logger_name)
        log_file = logging.FileHandler(log_file_name)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(log_file_format))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(log_console_format))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)
