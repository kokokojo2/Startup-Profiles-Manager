from base.app import Application
from script.service import IntegrityChecker

if __name__ == '__main__':
    checker = IntegrityChecker()
    checker.check()

    app = Application()
    app.run()
