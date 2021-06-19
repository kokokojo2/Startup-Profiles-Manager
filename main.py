import eel
import app.mid_level_func
from base.service import IntegrityChecker

if __name__ == '__main__':
    checker = IntegrityChecker()
    checker.check()

    eel.init('front')
    eel.start('templates/detail_profile.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron.exe', '.'],
              jinja_templates='templates')
