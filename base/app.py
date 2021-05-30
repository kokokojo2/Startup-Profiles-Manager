from base.data_classes import Profile, ProfileEntry
from db.db_manager import DB
from script.startup import StartupManager
from base.validator import Validator


class Application:
    """
    This class encapsulates functions that communicate with user and handle main procedures of an app.
    """

    def get_object_from_list(self, objects_list):
        for index, obj in enumerate(objects_list):
            print(f'[{index}][{obj.name}]')

        try:
            option = int(input())
            obj = objects_list[option]
            return obj
        except (ValueError, IndexError):
            print('Enter a valid index from a given list.')

    def run_profile(self):
        # TODO: add docstring

        while True:
            print('Select profile to launch:')

            startup_manager = StartupManager()
            db_manager = DB()
            profile_obj = self.get_object_from_list(db_manager.get_profile_list())

            if profile_obj is not None:
                print('Trying to launch config entries...')
                launched_number = startup_manager.launch_profile(profile_obj)
                print(f'Completed. Launched {launched_number} of {len(profile_obj.entries)} programs in your profile.')

                break

    def create_profile(self):
        # TODO: add docstring

        validator = Validator()
        db_manager = DB()

        while True:
            name = input('Enter a name of a new profile: ')
            if validator.bool_validate_name(name):
                new_profile = Profile(name)
                break

        option = input('Create a profile entry? [y/n]: ')
        if option == 'y':
            new_profile.entries = self.create_profile_entries()

        db_manager.save_profile(new_profile)

        print(f'Created profile:\n{new_profile}')
        print(f'Profile saved to database. You can launch it any time from main menu.')

    def create_profile_entries(self):
        # TODO: add docstring

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
                        entries.append(new_entry)
                        break

                option = input('Would you like to create another entry? [y/n]: ')

                if option != 'y':
                    break

        return entries

    def manage_profile(self):
        # TODO: add docstring
        db_manager = DB()
        profiles = db_manager.get_profile_list()

        while True:
            print('Select a profile: ')

            profile_obj = self.get_object_from_list(profiles)

            if profile_obj is not None:
                print(profile_obj)

                while True:
                    print('[1][Edit name]\n[2][Add entry]\n[3][Edit entry]\n[4][Delete entry]\n[5][Delete profile]\n['
                          '6][Exit to main menu]')
                    option = 0

                    try:
                        option = int(input('Choose one option: '))
                    except ValueError:
                        print('Enter a valid option.')

                    if option == 1:
                        new_name = input('Enter a new profile name: ')
                        # TODO: add a loop for bad name
                        # TODO: call validator for a name and save new obj
                    if option == 2:
                        # TODO: call add entry function and update profile
                        pass
                    if option == 3:
                        while True:
                            print('Choose entry to edit it:')
                            entry = self.get_object_from_list(profile_obj.entries)
                            if entry is not None:
                                break
                        self.edit_entry(entry)

                    if option == 4:
                        while True:
                            print('Choose entry to delete it:')
                            entry = self.get_object_from_list(profile_obj.entries)
                            if entry is not None:
                                break

                        db_manager.delete_profile_entry(entry)

                    if option == 5:
                        option = input('Are you sure want to delete whole profile? [y/n]: ')

                        if option == 'y':
                            db_manager.delete_profile(profile_obj)

                    if option == 5:
                        break

    def edit_entry(self, entry):
        while True:
            print('Choose one option:\n[1][Change name]\n[2][Change priority]\n[3][Change path to '
                  'exe][4][Enable\\Disable]\n')
            option = 0
            db_manager = DB()

            try:
                option = int(input())
            except ValueError:
                print('Enter a valid option.')

            # TODO: add whiles if mistakes
            if option == 1:
                new_name = input('Enter new name for a profile: ')
                # TODO: call validator and save new obj

            if option == 2:
                new_priority = input('Enter new priority as an integer: ')
                # TODO: call validator and save new obj

            if option == 3:
                new_path = input('Enter new path using "\\" to distinguish locations: ')
                # TODO: call validator and save new obj

            if option == 4:
                option = input(
                    f'This entry is now {"disabled" if entry.disabled else "enabled"}. Change to the opposite? [y/n]')
                if option == 'y':
                    entry.disabled = not entry.disabled

            db_manager.update_profile_entry(entry)

    def run(self):
        """
        Entry point of a console version of an app.
        """
        while True:
            print('Choose one option:')
            print('[1][Launch profile]\n[2][Create profile]\n[3][Manage my profiles]\n[4][Exit]\n')
            option = 0
            try:
                option = int(input())
            except ValueError:
                print('Enter a valid option.')

            if option == 1:
                self.run_profile()
                
            if option == 2:
                self.create_profile()

            if option == 3:
                self.manage_profile()

            if option == 4:
                break
