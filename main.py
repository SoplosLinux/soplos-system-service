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


def relaunch_as_root():
    """Relaunch with pkexec if not running as root, passing all required env vars."""
    if os.geteuid() == 0:
        return

    script = os.path.abspath(sys.argv[0])

    env_vars = {}
    for key in ('DISPLAY', 'XAUTHORITY', 'XDG_CURRENT_DESKTOP', 'XDG_SESSION_TYPE',
                'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION', 'DBUS_SESSION_BUS_ADDRESS',
                'LANG', 'LANGUAGE', 'LC_ALL', 'HOME', 'USER',
                'SOPLOS_SYSTEM_SERVICE_LANG'):
        val = os.environ.get(key)
        if val:
            env_vars[key] = val
    # Prevent GTK from trying to connect to ibus as root, which produces warnings.
    env_vars['GTK_IM_MODULE'] = 'gtk-im-context-simple'

    # Detect theme as regular user before becoming root.
    # As root, xfconf-query and gsettings query root's empty config, not the user's.
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
        from core.environment import EnvironmentDetector
        color_scheme = EnvironmentDetector().detect_all().get('theme_type', 'dark')
        env_vars['SOPLOS_COLOR_SCHEME'] = color_scheme
    except Exception:
        pass

    args = ['pkexec', 'env']
    for key, val in env_vars.items():
        args.append(f'{key}={val}')
    args += [sys.executable, script] + sys.argv[1:]

    try:
        os.execvp('pkexec', args)
    except Exception as e:
        dialog = Gtk.MessageDialog(
            parent=None,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text='Root privileges required',
        )
        dialog.format_secondary_text(str(e))
        dialog.run()
        dialog.destroy()
        sys.exit(1)


def main():
    relaunch_as_root()

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
