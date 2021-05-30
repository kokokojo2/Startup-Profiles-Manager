import unittest
from os import path

from base.validator import Validator
import config


class ValidatorTestCase(unittest.TestCase):

    def setUp(self):
        self.validator = Validator()

    def test_name_validation(self):

        case1 = ''
        case2 = 'fsdfhgggggggggggggggggggggooiwehfnddddddddddddddddddddddddddddddddddfndjf'
        case3 = 'Valid name'

        self.assertEqual(False, self.validator.bool_validate_name(case1))
        self.assertEqual(True, self.validator.bool_validate_name(case3))
        self.assertEqual(False, self.validator.bool_validate_name(case2))

    def test_priority_validation(self):
        case1 = '2'
        case2 = 'kebab'
        case3 = '2v'

        self.assertEqual(2, self.validator.get_valid_priority(case1))
        self.assertEqual(None, self.validator.get_valid_priority(case2))
        self.assertEqual(None, self.validator.get_valid_priority(case3))

    def test_path_validation(self):

        case1 = 'mockup_resources\\1.pdf'
        case2 = 'mockup_resources\\3.exe'
        case3 = 'mockup_resources\\not_existing_sub_folder\\23.exe'
        case4 = 'mockup_resources\\3.lnk'

        self.assertEqual(None, self.validator.get_valid_path(case1))
        self.assertEqual(case2, self.validator.get_valid_path(case2))
        self.assertEqual(None, self.validator.get_valid_path(case3))
        self.assertEqual(path.join(config.APPLICATION_ROOT, case2), self.validator.get_valid_path(case4))


if __name__ == '__main__':
    unittest.main()
