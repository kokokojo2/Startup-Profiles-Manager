import unittest

from db.db_manager import DB
from base.classes import Profile, ProfileEntry


class TestDBManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = DB('test.sqlite3')
        self.db_manager.create_default_structure()

    def tearDown(self):
        self.db_manager.drop()

    def test_save_profile(self):
        pr1 = Profile('Work',
                      [
                          ProfileEntry('Pycharm', 1, 'none'),
                          ProfileEntry('Telegram', 4, 'none'),
                          ProfileEntry('Solo', 3, 'none'),
                          ProfileEntry('CS', 2, 'none'),
                          ProfileEntry('Google', 12, 'none')
                      ])
        self.db_manager.save_profile(pr1)
        profiles_list = self.db_manager.get_profile_list()

        self.assertEqual(profiles_list[0].name, pr1.name)


if __name__ == '__main__':
    unittest.main()
