import eel


from base.app import Application
from base.service import IntegrityChecker

if __name__ == '__main__':
    eel.init('front')
    eel.start('main_menu.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron.exe', '.'])
