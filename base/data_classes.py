from dataclasses import dataclass
from beautifultable import BeautifulTable


@dataclass
class ProfileEntry:
    """
    This class represents a single entry of a profile such as an app or etc.
    """

    name: str
    priority: int
    launch_time: int = 0
    executable_path: str = None
    id: int = None
    disabled: bool = False

    def __str__(self):
        table = BeautifulTable()
        table.columns.header = ['Name', 'Enabled', 'Priority', 'Timeout', 'Path to executable']

        if self.disabled:
            enabled = 'No'
        else:
            enabled = 'Yes'

        table.rows.append([self.name, enabled, self.priority, self.launch_time, self.executable_path])

        return str(table)


@dataclass
class Profile:
    """
    This class represents a user-configured startup profile.
    """

    name: str
    entries: list[ProfileEntry] = None
    id: int = None
    timeout_mode: bool = False

    def __str__(self):
        table = BeautifulTable()
        if self.timeout_mode:
            table.columns.header = ['Name', 'Enabled', 'Priority', 'Timeout', 'Path to executable']
        else:
            table.columns.header = ['Name', 'Enabled', 'Priority', 'Path to executable']

        for entry in self.entries:
            if entry.disabled:
                enabled = 'No'
            else:
                enabled = 'Yes'

            if self.timeout_mode:
                table.rows.append([entry.name,enabled, entry.priority, entry.launch_time, entry.executable_path])
            else:
                table.rows.append([entry.name,enabled, entry.priority, entry.executable_path])

        return f'Profile "{self.name}".\n-Timeout mode: {"enabled" if self.timeout_mode else "disabled"}.\nEntries:\n{table}'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Settings(metaclass=Singleton):
    """
    This class encapsulates user settings in one object.
    """

    def __init__(self, close_after_launch=False, enable_startup=True):
        self.close_after_launch = close_after_launch
        self.enable_startup = enable_startup

