import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from pathlib import Path

from core import APP_ID, APP_VERSION
from core.environment import get_environment_detector
from core.theme_manager import ThemeManager
from ui.main_window import MainWindow


class SoplosSystemServiceApp(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        )
        self._window = None
        self._base_dir = Path(__file__).parent.parent

    def do_startup(self):
        Gtk.Application.do_startup(self)
        env_detector = get_environment_detector()
        theme_manager = ThemeManager(self._base_dir, env_detector)
        theme_manager.load_and_apply()
        self._env_detector = env_detector

        action_quit = Gio.SimpleAction.new('quit', None)
        action_quit.connect('activate', lambda a, p: self.quit())
        self.add_action(action_quit)
        self.set_accels_for_action('app.quit', ['<Control>q', '<Control>w'])

    def do_command_line(self, command_line):
        self.activate()
        return 0

    def do_activate(self):
        if not self._window:
            self._window = MainWindow(self, self._env_detector)
        self._window.present()
