import json

import eel
import logging

import config
from .state_management import StateManager
from base.managers import DB, StartupManager, SettingsManager
from base.data_classes import Settings, Profile, ProfileEntry
from base.validator import Validator


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


@eel.expose
def save_profile(profile_json):
    logger.info('Performing validation and saving profile...')
    parsed_profile = json.loads(profile_json)
    validator = Validator()

    messages = {}
    valid_name = validator.bool_validate_name(parsed_profile['name'])
    if not valid_name[0]:
        messages['name'] = valid_name[1]

    for entry_raw in parsed_profile['entries']:
        validation_result = {
            'valid_name': validator.bool_validate_name(entry_raw['name']),
            'valid_priority': validator.get_valid_priority(entry_raw['priority']),
            'valid_launch_time': validator.get_valid_timeout(entry_raw['launch_time']),
            'valid_exe': validator.get_valid_path(entry_raw['executable_path']),
        }
        entry_raw['validation'] = validation_result

    for entry_raw in parsed_profile['entries']:
        result_dict = entry_raw['validation']
        if not result_dict['valid_name'][0]:
            messages['name'] = result_dict['valid_name'][1]

        if not result_dict['valid_priority'][0]:
            messages['priority'] = result_dict['valid_priority'][1]

        if not result_dict['valid_launch_time'][0]:
            messages['launch_time'] = result_dict['valid_launch_time'][1]

        if not result_dict['valid_exe'][0]:
            messages['path'] = result_dict['valid_exe'][1]

    if len(messages.keys()) == 0:
        pr = Profile(
            parsed_profile['name'],
            entries=[],
            timeout_mode=parsed_profile['timeout_mode'],
            id=parsed_profile['id'],
            )

        for entry_raw in parsed_profile['entries']:
            entry = ProfileEntry(
                entry_raw['validation']['valid_name'][1],
                entry_raw['validation']['valid_priority'][1],
                launch_time=entry_raw['validation']['valid_launch_time'][1],
                executable_path=entry_raw['validation']['valid_exe'][1],
                id=entry_raw['id'],
            )
            pr.entries.append(entry)

        db_manager = DB()
        db_manager.save_profile(pr)

        return json.dumps({'status': 'saved'})

    json_serializable_messages = {'status': 'error', 'messages': []}
    for message in messages.values():
        json_serializable_messages['messages'].append('ⓘ ' + message)

    return json.dumps(json_serializable_messages)
