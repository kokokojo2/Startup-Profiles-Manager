import os


# directory configuration

APPLICATION_ROOT = os.getcwd()
LOGS_DIR = os.path.join(APPLICATION_ROOT, 'logfiles')


# logging configuration

MAIN_LOG_FILENAME = 'main_log' + '.log'
MESSAGE_FORMAT_TO_FILE = '%(asctime)s - %(name)s:%(levelname)s: in %(funcName)s: %(message)s'
# TODO: change to contain only user significant data
MESSAGE_FORMAT_TO_CONSOLE = '%(asctime)s - %(name)s:%(levelname)s: in %(funcName)s: %(message)s'

DB_LOGGER_NAME = 'Database manager'
STARTUP_LOGGER_NAME = 'Startup scripts'
VALIDATOR_LOGGER_NAME = 'Validator'

MAIN_LOG_PATH = os.path.join(LOGS_DIR, MAIN_LOG_FILENAME)


# Database configuration

DATABASE_FILENAME = 'db' + 'sqlite3'
