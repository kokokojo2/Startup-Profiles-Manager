
class Application:
    """
    This class encapsulates functions that communicate with user and handle main procedures of an app.
    """

    def run(self):
        """
        Entry point of a console version of an app.
        """
        while True:
            print('Choose one option:')
            print('[1][Run profile]\n[2][Create profile]\n[3][Manage my profiles]\n[4][Exit]\n')
            option = 0
            try:
                option = int(input())
            except ValueError:
                print('Enter a valid option.')

            if option == 1:
                pass
                # TODO: get profile list and print it, then run selected one

            if option == 2:
                pass
                # TODO: call procedure of profile creation

            if option == 3:
                pass
                # TODO: get profile list, then run management tool

            if option == 4:
                break
