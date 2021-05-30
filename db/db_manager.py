import sqlite3
import logging

import config
from base.data_classes import Profile, ProfileEntry


# singleton class
class DB:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DB, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.db_name = config.DATABASE_FILENAME
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
                profile_name VARCHAR(64)  
            );
            
            CREATE TABLE IF NOT EXISTS ProfileEntries(
                entry_id INTEGER PRIMARY KEY,
                entry_name VARCHAR(64),
                executable_path TEXT,
                priority INTEGER, 
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
            self.update_profile_metadata(profile_object)
        else:
            self.logger.info(f'Updating profile with name - {profile_object.name}.')
            self.save_profile_metadata(profile_object)

        profile_object.id = self.cursor.lastrowid
        for entry in profile_object.entries:
            if entry.id is not None:
                self.logger.info(f'Updating profile entry with name - {entry.name} of {profile_object.name} profile.')
                self.__update_profile_entry(entry)
            else:
                self.logger.info(f'Saving profile entry with name - {entry.name} of {profile_object.name} profile.')
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

        self.cursor.execute('INSERT INTO ProfileMeta (profile_name) VALUES(?)',
                            (profile_object.name, ))

    def update_profile_metadata(self, profile_object):
        """
        Updates a row in ProfileMeta with profile_object.id. Should be used only if object exists in a database.
        :param profile_object: Profile instance
        :return:
        """
        self.cursor.execute('UPDATE ProfileMeta SET profile_name = ? WHERE profile_id = ?',
                            (profile_object.name, profile_object.id))

    def save_profile_entry(self, profile_entry, profile_obj):
        """
        Saves given profile entry.
        :param profile_obj: instance of Profile class
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.cursor.execute('INSERT INTO ProfileEntries (entry_name, executable_path, priority, profile_id) VALUES(?, ?, ?, ?)',
                            (profile_entry.name, profile_entry.executable_path, profile_entry.priority, profile_obj.id))

    def __update_profile_entry(self, profile_entry):
        """
        Updates given profile entry.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.cursor.execute('UPDATE ProfileEntries SET entry_name=?, executable_path=?,  priority=? WHERE entry_id = ?',
                            (profile_entry.name, profile_entry.executable_path, profile_entry.priority, profile_entry.id))

    def update_profile_entry(self, profile_entry):
        """
        Updates given profile entry. Establish connection automatically.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.get_cursor()
        self.cursor.execute('UPDATE ProfileEntries SET entry_name=?, executable_path=?,  priority=? WHERE entry_id = ?',
                            (profile_entry.name, profile_entry.executable_path, profile_entry.priority,
                             profile_entry.id))
        self.connection.commit()
        self.close_connection()

    def delete_profile_entry(self, profile_entry):
        """
        Deletes given profile entry.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.get_cursor()
        self.cursor.execute('DELETE FROM ProfileEntries WHERE entry_id = ?', (profile_entry.id, ))
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
        self.cursor.execute('DELETE FROM ProfileMeta WHERE profile_id = ?', (profile_object.id, ))
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
            profile_obj = Profile(entry[1], id=entry[0])
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
        self.cursor.execute('SELECT * FROM ProfileEntries WHERE profile_id = ?', (profile_obj.id, ))
        raw_entries_list = self.cursor.fetchall()

        entries_list = []
        for raw_entry in raw_entries_list:
            entry = ProfileEntry(raw_entry[1], raw_entry[3], executable_path=raw_entry[2], id=raw_entry[0])
            entries_list.append(entry)

        self.connection.commit()
        self.close_connection()

        return entries_list
