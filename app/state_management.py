class Pages:
    HOME = 0
    CREATE_PROFILE = 1
    LAUNCH_PROFILE = 2
    LAUNCH_IN_PROGRESS = 3
    CHOOSE_PROFILE = 4
    PROFILE_DETAIL = 5
    ABOUT = 6


class StateManager:
    current_page = Pages.HOME

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StateManager, cls).__new__(cls)

        return cls.instance
