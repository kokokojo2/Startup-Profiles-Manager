import sqlite3
import logging
import json
import winreg
import os
import win32com.client as win_client
from subprocess import Popen
from time import sleep


import config
from base.data_classes import Profile, ProfileEntry, Settings


# singleton class
class DB:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DB, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.db_name = config.DATABASE_FULL_PATH
        self.connection = None
        self.cursor = None

        self.logger = logging.getLogger(config.DB_LOGGER_NAME)
        log_file = logging.FileHandler(config.MAIN_LOG_PATH)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def connect(self):
        # TODO: add an try-except block
        self.connection = sqlite3.connect(self.db_name)

    def get_cursor(self):
        self.connect()
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys = ON')

    def close_connection(self):

        try:
            self.cursor.close()
        except AttributeError or sqlite3.ProgrammingError:
            self.logger.warning('Trying to close cursor that does not exist.', exc_info=True)

        try:
            self.connection.close()
        except AttributeError or sqlite3.ProgrammingError:
            self.logger.warning('Trying to close cursor that does not exist.', exc_info=True)

    def create_default_structure(self):
        self.get_cursor()

        self.cursor.executescript(
            '''
            CREATE TABLE IF NOT EXISTS ProfileMeta (
                profile_id INTEGER PRIMARY KEY,
                profile_name VARCHAR(64),
                timeout_mode INTEGER 
            );

            CREATE TABLE IF NOT EXISTS ProfileEntries(
                entry_id INTEGER PRIMARY KEY,
                entry_name VARCHAR(64),
                executable_path TEXT,
                priority INTEGER,
                disabled INTEGER,
                launch_time FLOAT,
                profile_id INTEGER,
                FOREIGN KEY (profile_id)
                REFERENCES ProfileMeta (profile_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE 
            );
            '''
        )
        self.connection.commit()

        self.logger.info('Default sql structure is created.')
        self.close_connection()

    def drop(self):
        self.get_cursor()
        self.cursor.executescript(
            '''
            DROP TABLE ProfileMeta;
            DROP TABLE ProfileEntries;
            '''
        )
        self.connection.commit()
        self.logger.info('Dropped all tables.')
        self.close_connection()

    def save_profile(self, profile_object):
        """
        Serializes profile obj with all entries and metadata to a database.
        Assumes that id field marks whether profile exists in a database or not.
        :param profile_object: Profile instance
        :return:
        """
        self.get_cursor()
        if profile_object.id is not None:
            self.logger.info(f'Updating profile with name - {profile_object.name} and id - {profile_object.id}.')
            self.__update_profile_metadata(profile_object)
        else:
            self.logger.info(f'Saving profile with name - {profile_object.name}.')
            self.save_profile_metadata(profile_object)
            profile_object.id = self.cursor.lastrowid

        for entry in profile_object.entries:
            if entry.id is not None:
                self.logger.info(f'Updating profile entry with name - {entry.name} of {profile_object.name} profile.')
                self.__update_profile_entry(entry)
            else:
                self.logger.info(
                    f'Saving profile entry with name - {entry.name}, id - {entry.id} of {profile_object.name} profile.')
                self.save_profile_entry(entry, profile_object)

        self.connection.commit()
        self.logger.info(f'Profile with name - {profile_object.name} is successfully saved.')
        self.close_connection()

    def save_profile_metadata(self, profile_object):
        """
        Inserts a new row to ProfileMeta. Should be used only if object does not yet exist in a database.
        :param profile_object: Profile instance
        :return:
        """

        self.cursor.execute('INSERT INTO ProfileMeta (profile_name, timeout_mode) VALUES(?, ?)',
                            (
                                profile_object.name,
                                int(profile_object.timeout_mode)
                            ))

    def __update_profile_metadata(self, profile_object):
        """
        Updates a row in ProfileMeta with profile_object.id. Should be used only if object exists in a database.
        :param profile_object: Profile instance
        :return:
        """
        self.cursor.execute('UPDATE ProfileMeta SET profile_name = ?, timeout_mode = ? WHERE profile_id = ?',
                            (
                                profile_object.name,
                                int(profile_object.timeout_mode),
                                profile_object.id
                            ))

    def update_profile_metadata(self, profile_object):
        """
        Updates a row in ProfileMeta with profile_object.id. Should be used only if object exists in a database.
        Establish connection automatically.
        :param profile_object: Profile instance
        :return:
        """
        self.get_cursor()
        self.cursor.execute('UPDATE ProfileMeta SET profile_name = ?, timeout_mode = ? WHERE profile_id = ?',
                            (
                                profile_object.name,
                                int(profile_object.timeout_mode),
                                profile_object.id
                            ))
        self.connection.commit()
        self.close_connection()

    def save_profile_entry(self, profile_entry, profile_obj):
        """
        Saves given profile entry.
        :param profile_obj: instance of Profile class
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.cursor.execute(
            'INSERT INTO ProfileEntries (entry_name, executable_path, priority, disabled, launch_time, profile_id) VALUES(?, ?, ?, ?, ?, ?)',
            (
                profile_entry.name,
                profile_entry.executable_path,
                profile_entry.priority,
                int(profile_entry.disabled),
                profile_entry.launch_time,
                profile_obj.id
            ))

    def __update_profile_entry(self, profile_entry):
        """
        Updates given profile entry.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.cursor.execute(
            'UPDATE ProfileEntries SET entry_name=?, executable_path=?,  priority=?, disabled=?, launch_time=? WHERE entry_id = ?',
            (
                profile_entry.name,
                profile_entry.executable_path,
                profile_entry.priority,
                int(profile_entry.disabled),
                profile_entry.launch_time,
                profile_entry.id
            ))

    def update_profile_entry(self, profile_entry):
        """
        Updates given profile entry. Establish connection automatically.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.get_cursor()
        self.cursor.execute(
            'UPDATE ProfileEntries SET entry_name=?, executable_path=?,  priority=?, disabled=?, launch_time=? WHERE entry_id = ?',
            (
                profile_entry.name,
                profile_entry.executable_path,
                profile_entry.priority,
                int(profile_entry.disabled),
                profile_entry.launch_time,
                profile_entry.id
            ))
        self.connection.commit()
        self.close_connection()

    def delete_profile_entry(self, profile_entry):
        """
        Deletes given profile entry.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.logger.info(f'Deleting entry {profile_entry} from database.')
        self.get_cursor()
        self.cursor.execute('DELETE FROM ProfileEntries WHERE entry_id = ?', (profile_entry.id,))
        self.connection.commit()
        self.close_connection()

    def delete_profile(self, profile_object):
        """
        Deletes a row in ProfileMeta with profile_object.id and all associated profile entries.
        :param profile_object: Profile instance
        :return:
        """
        self.get_cursor()
        self.logger.info(f'Deleting profile with name - {profile_object.name} and id - {profile_object.id}.')
        self.cursor.execute('DELETE FROM ProfileMeta WHERE profile_id = ?', (profile_object.id,))
        self.connection.commit()
        self.close_connection()

    def get_profile_list(self):
        """
        Selects all profiles from a database.
        :return: list of profiles
        """
        self.get_cursor()
        self.logger.info('Getting a list of profiles.')
        self.cursor.execute('SELECT * FROM ProfileMeta')
        raw_profile_list = self.cursor.fetchall()
        self.close_connection()

        profile_list = []
        for entry in raw_profile_list:
            profile_obj = Profile(entry[1], id=entry[0], timeout_mode=bool(entry[2]))
            profile_obj.entries = self.get_profile_entries(profile_obj)
            profile_list.append(profile_obj)

        return profile_list

    def get_profile_entries(self, profile_obj):
        """
        Selects all entries of a given profile.
        :param profile_obj: instance of Profile
        :return: Profile object with entries inside
        """
        self.get_cursor()
        self.logger.info(f'Getting profile entries of {profile_obj.name} profile.')
        self.cursor.execute('SELECT * FROM ProfileEntries WHERE profile_id = ?', (profile_obj.id,))
        raw_entries_list = self.cursor.fetchall()

        entries_list = []
        for raw_entry in raw_entries_list:
            entry = ProfileEntry(
                raw_entry[1],
                raw_entry[3],
                executable_path=raw_entry[2],
                id=raw_entry[0],
                disabled=bool(raw_entry[4]),
                launch_time=raw_entry[5]
            )
            entries_list.append(entry)

        self.connection.commit()
        self.close_connection()

        return entries_list

    def get_profile(self, profile_id):
        """
        Selects profile metadata and entries of a given profile id.
        :param profile_id: int representing id of the profile in database
        :return: instance of Profile
        """

        self.get_cursor()
        self.cursor.execute('SELECT * FROM ProfileMeta WHERE profile_id = ?', (profile_id,))
        raw_profile_meta = self.cursor.fetchone()

        profile = Profile(raw_profile_meta[1], id=raw_profile_meta[0], timeout_mode=bool(raw_profile_meta[2]))
        profile.entries = self.get_profile_entries(profile)

        return profile


class SettingsManager:
    """
    This class encapsulates functions that manage user settings of an app.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SettingsManager, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(config.SETTINGS_LOGGER_NAME)
        log_file = logging.FileHandler(config.MAIN_LOG_PATH)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def satisfy_and_save(self, new_setting_obj):
        """
        This function checks new settings for changes, and makes according changes to a system.
        :param new_setting_obj: instance of Settings class which represents new settings input from user.
        """
        old_settings = self.get_settings()

        if old_settings.enable_startup != new_setting_obj.enable_startup:
            if new_setting_obj.enable_startup:
                self.make_startup_shortcut()
            else:
                self.remove_startup_shortcut()

        self.write_settings(new_setting_obj)

    def make_startup_shortcut(self):
        """
        This function makes a shortcut of a script and ads it to a windows startup folder.
        """
        self.logger.info('Adding shortcut to a windows startup folder.')
        folder_path = os.path.join(os.path.expanduser('~'),
                                   'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
                                   'StartupManager.lnk'
                                   )
        shell = win_client.Dispatch('WScript.Shell')
        link = shell.CreateShortCut(folder_path)
        # TODO: check after build
        link.Targetpath = config.EXECUTABLE_FULL_PATH
        link.save()

    def remove_startup_shortcut(self):
        """
        This function deletes shortcut from a windows startup folder.
        """
        self.logger.info('Removing shortcut from a windows startup folder.')
        folder_path = os.path.join(os.path.expanduser('~'),
                                   'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
                                   'StartupManager.lnk'
                                   )
        try:
            os.remove(folder_path)
        except FileNotFoundError:
            self.logger.info('Startup windows folder does not contain shortcut, so unable to remove it.')

    def write_settings(self, setting_obj):
        """
        This function serializes settings object to a settings file.
        :param setting_obj: instance of Settings class
        """
        self.logger.info('Serializing settings object to a file...')
        serialized_settings = f'{{"close_after_launch": {"true" if setting_obj.close_after_launch else "false"}, ' \
                              f'"enable_startup": {"true" if setting_obj.enable_startup else "false"}}}'

        with open(config.SETTINGS_FULL_PATH, 'w') as f:
            f.write(serialized_settings)

        self.logger.info('Success')

    def get_settings(self):
        """
        Read json settings from class and create singleton object with settings.
        :return: settings object with parsed settings
        """
        self.logger.info('Trying to read and parse settings file from file.')
        try:
            with open(config.SETTINGS_FULL_PATH, 'r') as f:
                raw_settings = f.read()
        except FileNotFoundError:
            self.logger.warning('Settings file does not exist. Check ordering of SettingsManager`s methods calls.')

        parsed_settings = json.loads(raw_settings)
        return Settings(parsed_settings['close_after_launch'], parsed_settings['enable_startup'])

    # old
    def __write_to_registry_file(self):
        """
        This function writes an entry to a windows startup registry in order to start this script with os.
        """
        self.logger.info('Trying save an entry to a registry file...')
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            config.WINDOWS_REGISTRY_KEY,
            0,
            winreg.KEY_ALL_ACCESS
        )
        winreg.SetValueEx(registry_key,
                          'startup_manager',
                          0,
                          winreg.REG_SZ,
                          config.EXECUTABLE_FULL_PATH
                          )
        winreg.CloseKey(registry_key)
        self.logger.info('Success.')

    # old
    def __remove_from_registry_file(self):
        """
        This function removes an entry from a windows registry file.
        """
        self.logger.info('Trying to delete entry from registry file...')
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            config.WINDOWS_REGISTRY_KEY,
            0,
            winreg.KEY_ALL_ACCESS
        )
        try:
            winreg.DeleteValue(registry_key, 'startup_manager')
        except WindowsError:
            self.logger.warning('Oops. Unexpected error occur while updating settings.')


# a singleton class
class StartupManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StartupManager, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(config.STARTUP_LOGGER_NAME)
        log_file = logging.FileHandler(config.MAIN_LOG_PATH)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def run_executable_from_path(self, profile_entry):
        """
        This method tells os to execute the executable file, path for which is specified intro profile_entry.executable_path.
        :param profile_entry: Instance of ProfileEntry class
        :return: True if file is launched successfully
        """
        self.logger.info(f'Trying to run executable from location - "{profile_entry.executable_path}"')

        try:
            result = Popen(profile_entry.executable_path)
            self.logger.info(f'Executable is successfully launched with process id - {result.pid}.')
            return True
        except (FileNotFoundError, OSError) as e:

            if isinstance(e, FileNotFoundError):
                self.logger.warning(f'The application with name "{profile_entry.name}" has not been found at location "{profile_entry.executable_path}". Please, update path in profile settings.')

            # the FileNotFoundError is a subclass of OSError
            if isinstance(e, OSError) and not isinstance(e, FileNotFoundError):
                self.logger.warning(f'Oops, something went wrong with the application with name "{profile_entry.name}". Check if the file on a specified location is an executable file.')

            return False

    def launch_profile(self, profile_obj):
        """
        This method launches every profile entry in a given Profile object, if profile_obj.disabled is not set to True.
        :param profile_obj: instance of Profile class
        :return: Number of success launches (for testing purposes).
        """
        self.logger.info('Launching profile...')

        num_of_success_runs = 0
        profile_obj.entries.sort(key=lambda x: x.priority)

        for i, entry in enumerate(profile_obj.entries):
            if not entry.disabled and entry.executable_path is not None:
                if self.run_executable_from_path(entry):
                    num_of_success_runs += 1

                if profile_obj.timeout_mode and i != len(profile_obj.entries) - 1:
                    print(f'Entry has a timeout of {entry.launch_time} minutes. Waiting...')
                    sleep(entry.launch_time * 60)

            else:
                self.logger.info(f'The profile entry with name "{entry.name}" is disabled.')

        return num_of_success_runs
