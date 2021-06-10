import time
import logging

import config
from base.data_classes import Profile, ProfileEntry
from base.managers import DB, StartupManager, SettingsManager
from base.validator import Validator


class Application:
    """
    This class encapsulates functions that communicate with user and handle main procedures of an app.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Application, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.db_name = config.DATABASE_FULL_PATH
        self.connection = None
        self.cursor = None

        self.logger = logging.getLogger(config.APP_LOGGER_NAME)
        log_file = logging.FileHandler(config.MAIN_LOG_PATH)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def get_object_from_list(self, objects_list):
        """
        This function is used for requesting user to choose one item from a given list.
        :param objects_list: list of objects to choose from
        :return: chosen object
        """
        if len(objects_list) == 0:
            print('There is no items to choose from. Please, create one first.')
            return -1

        else:
            for index, obj in enumerate(objects_list):
                print(f'[{index}][{obj.name}]')
            print(f'[-1][Exit to previous menu]')

            try:
                option = int(input())
                obj = objects_list[option]
                if option == -1:
                    return option

                if option < -1:
                    print('Enter a valid index from a given list.')
                    return None

                return obj
            except (ValueError, IndexError):
                print('Enter a valid index from a given list.')

    def run_profile(self):
        """
        Procedure that launches every enabled entry in a selected by user profile.
        """
        startup_manager = StartupManager()
        db_manager = DB()
        settings_manager = SettingsManager()

        while True:
            print('Select profile to launch:')

            profile_obj = self.get_object_from_list(db_manager.get_profile_list())
            if isinstance(profile_obj, int):
                break

            if profile_obj is not None:
                print(f'Running {profile_obj}')
                self.logger.info(f'Running profile with name "{profile_obj.name}" and id - {profile_obj.id}')

                launched_number = startup_manager.launch_profile(profile_obj)
                print(f'Completed. Launched {launched_number} of {len(profile_obj.entries)} programs in your profile.')
                self.logger.info(f'Completed. Launched {launched_number} of {len(profile_obj.entries)} programs.')
                break

        if settings_manager.get_settings().close_after_launch:
            print('This program is configured to finish automatically after profile launch.')
            print('It will finish in:\n')
            for i in reversed(range(3)):
                print(f'{i} seconds.')
                time.sleep(1)

            return -1

    def create_profile(self):
        """
        Procedure that handles creation of profile with entries from user input.
        """

        validator = Validator()
        db_manager = DB()

        self.logger.info('Creating new profile...')
        while True:
            name = input('Enter a name of a new profile: ')
            if validator.bool_validate_name(name):
                new_profile = Profile(name, entries=[])
                break

        option = input('Do you want this profile to launch with delay after each entry? This option is recommended for '
                       'decreasing system resources usage. (You can change it later) [y/n]: ')
        if option == 'y':
            new_profile.timeout_mode = True

        option = input('Create a profile entry? [y/n]: ')
        if option == 'y':
            self.logger.info('Creating entries for profile...')
            new_profile.entries = self.create_profile_entries(new_profile.timeout_mode)

        db_manager.save_profile(new_profile)

        print(f'Created profile:\n{new_profile}')
        print(f'Profile saved to database. You can launch it any time from main menu.')

    def create_profile_entries(self, slow_mode):
        """
        Procedure that handles entries creation.
        :return: list of created profile entries
        """

        entries = []
        validator = Validator()

        while True:
            name = input('Enter a name of an entry. Typically it is a name of a associated program:\n')
            priority = input('Enter a priority for an entry using integer value (smaller number represents higher '
                             'priority): ')

            if validator.bool_validate_name(name) and validator.get_valid_priority(priority) is not None:
                new_entry = ProfileEntry(name, validator.get_valid_priority(priority))

                while True:
                    exe_path = input('Enter a full path for actual executable file of a program or its link:\n')
                    exe_path_valid = validator.get_valid_path(exe_path)

                    if exe_path_valid is not None:
                        new_entry.executable_path = exe_path_valid
                        break

                while slow_mode:
                    timeout = input('Enter a timeout for entry in minutes as an integer or float. Program will wait '
                                    'this amount of time before launching next entry. Usually it is a time that entry '
                                    'require to start itself.')
                    timeout_valid = validator.get_valid_timeout(timeout)

                    if timeout_valid is not None:
                        new_entry.launch_time = timeout_valid
                        break

                entries.append(new_entry)
                self.logger.info(f'Entry\n{new_entry} successfully created.')

                option = input('Would you like to create another entry? [y/n]: ')
                if option != 'y':
                    break

        return entries

    def manage_profile(self):
        """
        Procedure that handles managing profile e.g. deleting, editing both profiles and entries and adding a new ones.
        """

        db_manager = DB()
        validator = Validator()
        profiles = db_manager.get_profile_list()

        while True:
            print('Select a profile: ')
            profile_obj = self.get_object_from_list(profiles)

            if profile_obj is not None:
                break

        while profile_obj != -1:
            self.logger.info('Managing existing profile...')

            print(profile_obj)
            print('[1][Edit name]\n[2][Enable/Disable timeout mode]\n[3][Add entry]\n[4][Edit entry]\n[5][Delete '
                  'entry]\n[6][Delete profile]\n[7][Exit to main menu]')
            option = 0

            try:
                option = int(input('Choose one option: '))
            except ValueError:
                print('Enter a valid option.')

            if option == 1:
                while True:
                    new_name = input('Enter a new profile name: ')
                    if validator.bool_validate_name(new_name):
                        break

                profile_obj.name = new_name
                db_manager.update_profile_metadata(profile_obj)
                self.logger.info(f'Profile name changed to {profile_obj.name}')

            if option == 2:
                option = input(
                    f'Would you like to {"disable" if profile_obj.timeout_mode else "enable"} timeout mode? [y/n]\nIf '
                    f'you enable timeout mode, check out a profile entries, you might want to correct some timeout '
                    f'amounts.\n ')

                if option == 'y':
                    profile_obj.timeout_mode = not profile_obj.timeout_mode
                    db_manager.update_profile_metadata(profile_obj)

            if option == 3:
                new_entries = self.create_profile_entries(profile_obj.timeout_mode)
                profile_obj.entries += new_entries
                db_manager.save_profile(profile_obj)

            if option == 4:
                while True:
                    print('Choose entry to edit it:')
                    entry = self.get_object_from_list(profile_obj.entries)
                    if entry is not None:
                        break

                if entry != -1:
                    self.edit_entry(entry)

            if option == 5:
                while True:
                    print('Choose entry to delete it:')
                    entry = self.get_object_from_list(profile_obj.entries)
                    if entry is not None:
                        break
                if entry != -1:
                    db_manager.delete_profile_entry(entry)

            if option == 6:
                option = input('Are you sure want to delete whole profile? [y/n]: ')

                if option == 'y':
                    db_manager.delete_profile(profile_obj)
                    print('Profile was deleted.')
                    return

            if option == 7:
                break

            if option == 4 or option == 5:
                profile_obj.entries = db_manager.get_profile_entries(profile_obj)

    def edit_entry(self, entry):
        """
        Procedure that handles editing of a profile entry fields. Is a sub-procedure of manage_profile procedure.
        :param entry: instance of ProfileEntry object that should be edited
        """

        self.logger.info('Editing existing entry...')
        while True:
            print('Choose one option:\n[1][Change name]\n[2][Change priority]\n[3][Change path to '
                  'exe]\n[4][Enable/Disable]\n[5][Change timeout]\n[6][Exit to previous menu]\n')
            option = 0
            db_manager = DB()
            validator = Validator()

            try:
                option = int(input())
            except ValueError:
                print('Enter a valid option.')

            if option == 1:
                self.logger.info('Changing name...')
                while True:
                    new_name = input('Enter new name for a profile: ')
                    if validator.bool_validate_name(new_name):
                        break

                entry.name = new_name

            if option == 2:
                self.logger.info('Changing priority...')

                while True:
                    new_priority = validator.get_valid_priority(input('Enter new priority as an integer: '))
                    if new_priority is not None:
                        break

                entry.priority = new_priority

            if option == 3:
                self.logger.info('Changing executable path...')

                while True:
                    new_path = validator.get_valid_path(input('Enter new path using "\\" to distinguish locations: '))
                    if new_path is not None:
                        break

                entry.executable_path = new_path

            if option == 4:
                self.logger.info('Disable/Enable...')

                option = input(
                    f'This entry is now {"disabled" if entry.disabled else "enabled"}. Change to the opposite? [y/n]: ')
                if option == 'y':
                    entry.disabled = not entry.disabled

            if option == 5:
                self.logger.info('Changing timeout number...')

                while True:
                    timeout = input('Enter new timeout in minutes. The program will wait this amount of time before '
                                    'launching next entry.')
                    timeout_valid = validator.get_valid_timeout(timeout)

                    if timeout_valid is not None:
                        break
                entry.launch_time = timeout_valid

            if option == 6:
                break

            db_manager.update_profile_entry(entry)

    def manage_setting(self):
        """
        This is
        :return:
        """
        settings_manager = SettingsManager()
        settings = settings_manager.get_settings()
        self.logger.info('Manage settings...')
        while True:
            print(f'Choose one option:\n[1][{"Disable" if settings.enable_startup else "Enable"} start with '
                  f'Windows]\n[2][{"Close" if not settings.close_after_launch else "Do not close"} after profile '
                  f'launch]\n[3][Exit to previous menu]\n')
            option = 0
            try:
                option = int(input())
            except ValueError:
                print('Enter a valid option.')

            if option == 1:
                settings.enable_startup = not settings.enable_startup

            if option == 2:
                settings.close_after_launch = not settings.close_after_launch

            if option == 3:
                break

            settings_manager.satisfy_and_save(settings)

    def run(self):
        """
        Entry point of a console version of an app.
        """
        self.logger.info('Main program execution started.')

        while True:
            print('Choose one option:')
            print('[1][Launch profile]\n[2][Create profile]\n[3][My profiles]\n[4][Settings]\n[5][Exit]\n')
            option = 0
            try:
                option = int(input())
            except ValueError:
                print('Enter a valid option.')

            if option == 1:
                if self.run_profile() == -1:
                    break

            if option == 2:
                self.create_profile()

            if option == 3:
                self.manage_profile()

            if option == 4:
                self.manage_setting()

            if option == 5:
                break
