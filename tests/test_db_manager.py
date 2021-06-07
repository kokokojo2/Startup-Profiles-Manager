import unittest

from db.db_manager import DB
from base.data_classes import Profile, ProfileEntry


class TestDBManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = DB()
        self.db_manager.create_default_structure()

    def tearDown(self):
        self.db_manager.drop()

    def test_save_profile(self):
        pr1 = Profile('Work',
                      [
                          ProfileEntry('Pycharm', 1, 32, 'C:\\Users\\Dmytro\\PycharmProjects\\StartupProfilesManager\\tests\\mockup_resources\\1.exe'),
                          ProfileEntry('Telegram', 4, 3242),
                          ProfileEntry('Solo', 3),
                          ProfileEntry('CS', 2, 23),
                          ProfileEntry('Google', 12, disabled=True)
                      ],
                      timeout_mode=True)

        self.db_manager.save_profile(pr1)
        profiles_list = self.db_manager.get_profile_list()

        self.assertEqual(profiles_list[0].name, pr1.name)

        for expected, from_db in zip(pr1.entries, profiles_list[0].entries):
            self.assertEqual(from_db.name, expected.name)
            self.assertEqual(from_db.priority, expected.priority)
            self.assertEqual(from_db.launch_time, expected.launch_time)
            self.assertEqual(from_db.executable_path, expected.executable_path)
            self.assertEqual(from_db.disabled, expected.disabled)


if __name__ == '__main__':
    unittest.main()
