import sqlite3
from sqlite3 import Error


class DB:

    def __init__(self, db_name=None):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        # TODO: add an try-except block
        self.connection = sqlite3.connect(self.db_name)

    def get_cursor(self):
        self.connect()
        self.cursor = self.connection.cursor()

    def close_connection(self):

        try:
            self.cursor.close()
        except AttributeError:
            # TODO: add logs here
            pass

        try:
            self.connection.close()
        except AttributeError:
            # TODO: add logs here
            pass

    def create_default_structure(self):
        self.get_cursor()

        self.cursor.executemany(
            '''
            CREATE TABLE ProfileMeta (
                profile_id INTEGER PRIMARY KEY,
                profile_name VARCHAR(64)  
            );
            
            CREATE TABLE ProfileEntries(
                entry_id INTEGER PRIMARY KEY,
                entry_name VARCHAR(128),
                executable_path TEXT,
                priority INTEGER, 
            );
            '''
        )
        self.close_connection()

    def drop(self):
        self.get_cursor()

        self.cursor.executemany(
            '''
            DROP TABLE ProfileMeta;
            DROP TABLE ProfileEntries;
            '''
        )
        self.close_connection()

    def save_profile(self, profile_object):
        """
        Serializes profile obj with all entries and metadata to a database.
        Assumes that id field marks whether profile exists in a database or not.
        :param profile_object: Profile instance
        :return:
        """
        pass

    def save_profile_metadata(self, profile_object):
        """
        Inserts a new row to ProfileMeta. Should be used only if object does not yet exist in a database.
        :param profile_object: Profile instance
        :return:
        """

    def update_profile_metadata(self, profile_object):
        """
        Updates a row in ProfileMeta with profile_object.id. Should be used only if object exists in a database.
        :param profile_object: Profile instance
        :return:
        """

    def save_profile_entry(self, profile_entry):
        """
        Saves given profile entry.
        :param profile_entry: named tuple with info about entry
        :return:
        """

    def update_profile_entry(self, profile_entry):
        """
        Updates given profile entry.
        :param profile_entry: named tuple with info about entry
        :return:
        """

    def delete_profile_entry(self, profile_entry):
        """
        Deletes given profile entry.
        :param profile_entry: named tuple with info about entry
        :return:
        """

    def delete_profile(self, profile_object):
        """
        Deletes a row in ProfileMeta with profile_object.id and all associated profile entries.
        :param profile_object: Profile instance
        :return:
        """

    def get_profile_list(self):
        """
        Selects all profile metas from a database.
        :return: list of profiles
        """

    def get_profile_entries(self, profile):
        """
        Selects all entries of a given profile.
        :param profile: instance of Profile
        :return: Profile object with entries inside
        """