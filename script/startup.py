from subprocess import Popen
import logging

# logging constants
# TODO: should be moved to a global config file
logger_name = 'Startup scripts'
log_file_name = 'main_log.log'
log_file_format = '%(asctime)s - %(name)s:%(levelname)s: in %(funcName)s: %(message)s'
log_console_format = '%(asctime)s - %(name)s:%(levelname)s: %(message)s'


# a singleton class
class StartupManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StartupManager, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        self.logger = logging.getLogger(logger_name)
        log_file = logging.FileHandler(log_file_name)
        error_stream = logging.StreamHandler()

        log_file.setLevel(logging.INFO)
        log_file.setFormatter(logging.Formatter(log_file_format))

        error_stream.setLevel(logging.WARNING)
        error_stream.setFormatter(logging.Formatter(log_console_format))

        self.logger.addHandler(log_file)
        self.logger.addHandler(error_stream)

        self.logger.setLevel(logging.DEBUG)

    def run_executable_from_path(self, profile_entry):
        """
        This method tells os to execute the executable file, path for which is specified intro profile_entry.executable_path.
        :param profile_entry: Instance of ProfileEntry class
        :return: True if file is launched successfully
        """
        self.logger.info(f'Trying to run executable from location - "{profile_entry.executable_path}"')

        try:
            result = Popen(profile_entry.executable_path)
            self.logger.info(f'Executable is successfully launched with process id - {result.pid}.')
            return True
        except (FileNotFoundError, OSError) as e:

            if isinstance(e, FileNotFoundError):
                self.logger.warning(f'The application with name "{profile_entry.name}" has not been found at location "{profile_entry.executable_path}". Please, update path in profile settings.')

            # the FileNotFoundError is a subclass of OSError
            if isinstance(e, OSError) and not isinstance(e, FileNotFoundError):
                self.logger.warning(f'Oops, something went wrong with the application with name "{profile_entry.name}". Check if the file on a specified location is an executable file.')

            return False

    def launch_profile(self, profile_obj):
        """
        This method launches every profile entry in a given Profile object, if profile_obj.disabled is not set to True.
        :param profile_obj: instance of Profile class
        :return: Number of success launches (for testing purposes).
        """
        self.logger.info('Launching profile...')

        num_of_success_runs = 0
        profile_obj.entries.sort(key=lambda x: x.priority)

        for entry in profile_obj.entries:
            if not entry.disabled and entry.executable_path is not None:
                if self.run_executable_from_path(entry):
                    num_of_success_runs += 1

            else:
                self.logger.info(f'The profile entry with name "{entry.name}" is disabled.')

        return num_of_success_runs
