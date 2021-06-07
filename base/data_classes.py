from dataclasses import dataclass


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
        return f'{self.name}, pr: {self.priority}, enabled: {not self.disabled}, {self.executable_path}'


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
        result = f'Profile "{self.name}".\nEntries:\n'
        for entry in self.entries:
            result += str(entry) + '\n'

        return f'Profile "{self.name}".\n-Timeout mode: {"enabled" if self.timeout_mode else "disabled"}.\nEntries:\n{table}'



