import json

import eel
import logging

import config
from .state_management import StateManager
from base.managers import DB, StartupManager, SettingsManager
from base.data_classes import Settings


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


@eel.expose
def get_profile_list():
    logger.info('Getting profile list for js call.')

    db_manager = DB()
    profiles = db_manager.get_profile_list()

    if len(profiles) == 0:
        return '{ "status": "NO PROFILES" }'
    json_serializable = []
    for profile in profiles:
        json_serializable.append(profile.get_json_dict())

    json_serializable = {'status': 'OK', 'data': json_serializable}

    return json.dumps(json_serializable)


@eel.expose
def launch_profile(profile_id):
    logger.info('Launching profile for js call...')

    db_manager = DB()
    startup_manager = StartupManager()
    current_profile = db_manager.get_profile(profile_id)

    startup_manager.launch_profile(current_profile)


@eel.expose
def get_profile_info(profile_id):
    logger.info('Getting profile for a js call.')

    db_manager = DB()
    profile = db_manager.get_profile(profile_id)
    json_serializable = {'meta': profile.get_json_dict()}

    raw_entries = []
    for entry in profile.entries:
        raw_entries.append(entry.get_json_dict())
    json_serializable['entries'] = raw_entries

    return json.dumps(json_serializable)


@eel.expose
def update_settings(settings_json):
    parsed_settings = json.loads(settings_json)
    settings = Settings(parsed_settings['close_after_launch'], parsed_settings['enable_startup'])

    settings_manager = SettingsManager()
    settings_manager.satisfy_and_save(settings)
