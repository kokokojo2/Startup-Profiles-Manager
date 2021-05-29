from dataclasses import dataclass


@dataclass
class ProfileEntry:
    """
    This class represents a single entry of a profile such as an app or etc.
    """

    name: str
    priority: int
    executable_path: str = None
    id: int = None
    disabled: bool = False


@dataclass
class Profile:
    """
    This class represents a user-configured startup profile.
    """

    name: str
    entries: list[ProfileEntry] = None
    id: int = None



