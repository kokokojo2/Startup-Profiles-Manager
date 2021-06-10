import os


# directory configuration
APPLICATION_ROOT = os.path.dirname(os.path.realpath(__file__))
# TODO: check if this stuff works with built .exe file
EXECUTABLE_FULL_PATH = os.path.join(APPLICATION_ROOT, 'main.py')  # temporary
LOGS_DIR = os.path.join(APPLICATION_ROOT, 'logfiles')

# logging configuration
MAIN_LOG_FILENAME = 'main_log' + '.log'
MESSAGE_FORMAT_TO_FILE = '%(asctime)s - %(name)s:%(levelname)s: in %(funcName)s: %(message)s'
MESSAGE_FORMAT_TO_CONSOLE = '%(asctime)s - %(name)s:%(levelname)s: in %(funcName)s: %(message)s'

DB_LOGGER_NAME = 'Database manager'
STARTUP_LOGGER_NAME = 'Startup scripts'
VALIDATOR_LOGGER_NAME = 'Validator'
INT_CHECKER_LOGGER_NAME = 'Integrity checker'
APP_LOGGER_NAME = 'User interface'
SETTINGS_LOGGER_NAME = 'User settings'

MAIN_LOG_PATH = os.path.join(LOGS_DIR, MAIN_LOG_FILENAME)

# Database configuration
DATABASE_FILENAME = 'db' + '.sqlite3'
DATABASE_PATH = os.path.join(APPLICATION_ROOT, 'data')
DATABASE_FULL_PATH = os.path.join(DATABASE_PATH, DATABASE_FILENAME)

# Settings file configuration
SETTINGS_NAME = 'settings.txt'
SETTINGS_PATH = os.path.join(APPLICATION_ROOT, 'data')
SETTINGS_FULL_PATH = os.path.join(SETTINGS_PATH, SETTINGS_NAME)

WINDOWS_REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
