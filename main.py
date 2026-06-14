#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import os
import sys
import signal
import atexit
import shutil


def cleanup_pycache():
    try:
        base_dir = os.path.dirname(os.path.abspath(globals().get('__file__') or sys.argv[0]))
        for root, dirs, _ in os.walk(base_dir):
            if '__pycache__' in dirs:
                try:
                    shutil.rmtree(os.path.join(root, '__pycache__'))
                except Exception:
                    pass
    except Exception:
        pass


atexit.register(cleanup_pycache)
def _signal_handler(*_):
    cleanup_pycache()
    sys.exit(0)


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def main():
    if not Gtk.init_check()[0]:
        print('Error: GTK could not be initialized.')
        sys.exit(2)

    from utils.strings import get_system_language, set_language
    lang = get_system_language()
    set_language(lang)

    from core.application import SoplosSystemServiceApp
    app = SoplosSystemServiceApp()
    sys.exit(app.run(sys.argv))


if __name__ == '__main__':
    main()
