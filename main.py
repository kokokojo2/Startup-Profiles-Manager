import config
import os
import eel

from base.before_imports_check import check

os.chdir(config.APPLICATION_ROOT)
check()  # make lazy initialization of loggers instead of this
from base.service import IntegrityChecker
import app.mid_level_func


if __name__ == '__main__':
    checker = IntegrityChecker()
    checker.check()

    eel.init('front')
    eel.start('templates/detail_profile.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron.exe', '.'],
              jinja_templates='templates')
