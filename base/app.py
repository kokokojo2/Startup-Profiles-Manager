from db.db_manager import DB
from script.startup import StartupManager


class Application:
    """
    This class encapsulates functions that communicate with user and handle main procedures of an app.
    """

    def run_profile(self):
        # TODO: add docstring

        while True:
            print('Select profile to launch:')

            db_manager = DB()
            startup_manager = StartupManager()
            profile_list = db_manager.get_profile_list()

            for index, profile in enumerate(profile_list):
                print(f'[{index}][{profile.name}]')

            valid_index = False
            try:
                option = int(input())
                profile_obj = profile_list[option]
                valid_index = True
            except (ValueError, IndexError):
                print('Enter a valid index from a given list.')

            if valid_index:
                print('Trying to launch config entries...')
                launched_number = startup_manager.launch_profile(profile_obj)
                print(f'Completed. Launched {launched_number} of {len(profile_obj.entries)} programs in your profile.')

                break

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
                pass
                # TODO: call procedure of profile creation

            if option == 3:
                pass
                # TODO: get profile list, then run management tool

            if option == 4:
                break
