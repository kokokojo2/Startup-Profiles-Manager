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

    @require_connection
    def create_default_structure(self):

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
                profile_id INTEGER,
                FOREIGN KEY (profile_id)
                REFERENCES ProfileMeta (profile_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE 

            );
            '''
        )

    @require_connection
    def drop(self):

        self.cursor.executemany(
            '''
            DROP TABLE ProfileMeta;
            DROP TABLE ProfileEntries;
            '''
        )

    @require_connection
    def save_profile(self, profile_object):
        """
        Serializes profile obj with all entries and metadata to a database.
        Assumes that id field marks whether profile exists in a database or not.
        :param profile_object: Profile instance
        :return:
        """
        if profile_object.id is not None:
            self.update_profile_metadata(profile_object)
        else:
            self.save_profile_metadata(profile_object)

        for entry in profile_object.entries:
            if entry.id is not None:
                self.update_profile_entry(entry)
            else:
                self.save_profile_entry(entry, profile_object)

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

    def update_profile_entry(self, profile_entry):
        """
        Updates given profile entry.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.cursor.execute('UPDATE ProfileEntries SET entry_name=?, executable_path=?,  priority=? WHERE entry_id = ?',
                            (profile_entry.name, profile_entry.executable_path, profile_entry.priority, profile_entry.id))

    @require_connection
    def delete_profile_entry(self, profile_entry):
        """
        Deletes given profile entry.
        :param profile_entry: instance of ProfileEntry class with info about entry
        :return:
        """
        self.cursor.execute('DELETE FROM ProfileEntries WHERE entry_id = ?', (profile_entry.id, ))

    @require_connection
    def delete_profile(self, profile_object):
        """
        Deletes a row in ProfileMeta with profile_object.id and all associated profile entries.
        :param profile_object: Profile instance
        :return:
        """
        self.cursor.execute('DELETE FROM ProfileMeta WHERE profile_id = ?', (profile_object.id, ))

    @require_connection
    def get_profile_list(self):
        """
        Selects all profile metas from a database.
        :return: list of profiles
        """
        self.cursor.execute('SELECT * FROM Profiles')
        raw_profile_list = self.cursor.fetchall()
        for entry in raw_profile_list:
            # TODO: finish when debugging
            pass

    @require_connection
    def get_profile_entries(self, profile_obj):
        """
        Selects all entries of a given profile.
        :param profile_obj: instance of Profile
        :return: Profile object with entries inside
        """
        self.cursor.execute('SELECT * FROM ProfilesEntries WHERE profile_id = ?', (profile_obj.id, ))
        # TODO: finish when debugging
