import eel
import logging

import config
from state_management import StateManager

logger = logging.getLogger(config.APP_LOGGER_NAME)
log_file = logging.FileHandler(config.MAIN_LOG_PATH)
error_stream = logging.StreamHandler()

log_file.setLevel(logging.INFO)
log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

error_stream.setLevel(logging.WARNING)
error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

logger.addHandler(log_file)
logger.addHandler(error_stream)

logger.setLevel(logging.DEBUG)


@eel.expose
def get_current_page_id():
    logger.info('Getting current page id...')
    state = StateManager()
    return state.current_page


@eel.expose
def update_current_page_id(page_id):
    logger.info('Updating current page id...')
    state = StateManager()
    state.current_page = int(page_id)
