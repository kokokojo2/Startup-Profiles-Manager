import unittest
from base.managers import StartupManager
from base.data_classes import Profile, ProfileEntry


class MyTestCase(unittest.TestCase):

    def test_singleton(self):
        s1 = StartupManager()
        s2 = StartupManager()

        self.assertIs(s1, s2)

    def test_launch_profile(self):
        startup_manager = StartupManager()
        success_num_expected = 2
        pr1 = Profile('Work',
                      [
                          ProfileEntry('Pycharm', 1),
                          ProfileEntry('VS setup', 4, executable_path=r'mockup_resources\1.exe'),
                          ProfileEntry('Just random pdf', 3, executable_path=r'mockup_resources\1.pdf'),
                          ProfileEntry('CS', 2, executable_path=r'mockup_resources\123134y2t34.exe'),
                          ProfileEntry('Viber Setup', 5, executable_path=r'mockup_resources\3.exe'),
                          ProfileEntry('LOL', 6, executable_path=r'mockup_resources\does_not_exist.exe', disabled=True),
                      ])

        success_num = startup_manager.launch_profile(pr1)
        self.assertEqual(success_num_expected, success_num)


if __name__ == '__main__':
    unittest.main()
