import config
import logging
import json
import winreg
import os
import win32com.client as win_client

from base.data_classes import Settings


class SettingsManager:
    """
    This class encapsulates functions that manage user settings of an app.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SettingsManager, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(config.SETTINGS_LOGGER_NAME)
        log_file = logging.FileHandler(config.MAIN_LOG_PATH)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_FILE))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(config.MESSAGE_FORMAT_TO_CONSOLE))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def satisfy_and_save(self, new_setting_obj):
        """
        This function checks new settings for changes, and makes according changes to a system.
        :param new_setting_obj: instance of Settings class which represents new settings input from user.
        """
        old_settings = self.get_settings()

        if old_settings.enable_startup != new_setting_obj.enable_startup:
            if new_setting_obj.enable_startup:
                self.make_startup_shortcut()
            else:
                self.remove_startup_shortcut()

        self.write_settings(new_setting_obj)

    def make_startup_shortcut(self):
        """
        This function makes a shortcut of a script and ads it to a windows startup folder.
        """
        self.logger.info('Adding shortcut to a windows startup folder.')
        folder_path = os.path.join(os.path.expanduser('~'),
                                   'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
                                   'StartupManager.lnk'
                                   )
        shell = win_client.Dispatch('WScript.Shell')
        link = shell.CreateShortCut(folder_path)
        # TODO: check after build
        link.Targetpath = config.EXECUTABLE_FULL_PATH
        link.save()

    def remove_startup_shortcut(self):
        """
        This function deletes shortcut from a windows startup folder.
        """
        self.logger.info('Removing shortcut from a windows startup folder.')
        folder_path = os.path.join(os.path.expanduser('~'),
                                   'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
                                   'StartupManager.lnk'
                                   )
        try:
            os.remove(folder_path)
        except FileNotFoundError:
            self.logger.info('Startup windows folder does not contain shortcut, so unable to remove it.')

    def write_settings(self, setting_obj):
        """
        This function serializes settings object to a settings file.
        :param setting_obj: instance of Settings class
        """
        self.logger.info('Serializing settings object to a file...')
        serialized_settings = f'{{"close_after_launch": {"true" if setting_obj.close_after_launch else "false"}, ' \
                              f'"enable_startup": {"true" if setting_obj.enable_startup else "false"}}}'

        with open(config.SETTINGS_FULL_PATH, 'w') as f:
            f.write(serialized_settings)

        self.logger.info('Success')

    def get_settings(self):
        """
        Read json settings from class and create singleton object with settings.
        :return: settings object with parsed settings
        """
        self.logger.info('Trying to read and parse settings file from file.')
        try:
            with open(config.SETTINGS_FULL_PATH, 'r') as f:
                raw_settings = f.read()
        except FileNotFoundError:
            self.logger.warning('Settings file does not exist. Check ordering of SettingsManager`s methods calls.')

        parsed_settings = json.loads(raw_settings)
        return Settings(parsed_settings['close_after_launch'], parsed_settings['enable_startup'])

    # old
    def __write_to_registry_file(self):
        """
        This function writes an entry to a windows startup registry in order to start this script with os.
        """
        self.logger.info('Trying save an entry to a registry file...')
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            config.WINDOWS_REGISTRY_KEY,
            0,
            winreg.KEY_ALL_ACCESS
        )
        winreg.SetValueEx(registry_key,
                          'startup_manager',
                          0,
                          winreg.REG_SZ,
                          config.EXECUTABLE_FULL_PATH
                          )
        winreg.CloseKey(registry_key)
        self.logger.info('Success.')

    # old
    def __remove_from_registry_file(self):
        """
        This function removes an entry from a windows registry file.
        """
        self.logger.info('Trying to delete entry from registry file...')
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            config.WINDOWS_REGISTRY_KEY,
            0,
            winreg.KEY_ALL_ACCESS
        )
        try:
            winreg.DeleteValue(registry_key, 'startup_manager')
        except WindowsError:
            self.logger.warning('Oops. Unexpected error occur while updating settings.')
