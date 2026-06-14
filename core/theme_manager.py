import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from pathlib import Path


class ThemeManager:

    def __init__(self, base_dir: Path, env_detector):
        self._base_dir = base_dir
        self._env_detector = env_detector

    def load_and_apply(self):
        themes_dir = self._base_dir / 'assets' / 'themes'
        system_dir = Path('/usr/share/soplos-system-services/themes')

        search = themes_dir if themes_dir.exists() else system_dir

        is_dark = self._env_detector.is_dark_theme
        theme_file = 'dark.css' if is_dark else 'light.css'

        # Load dark/light first so @define-color variables are available
        theme_path = search / theme_file
        if theme_path.exists():
            try:
                provider = Gtk.CssProvider()
                provider.load_from_path(str(theme_path))
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e:
                print(f"Error loading {theme_file}: {e}")

        # Load base.css after so Soplos structural classes override widget defaults
        base_path = search / 'base.css'
        if base_path.exists():
            try:
                provider = Gtk.CssProvider()
                provider.load_from_path(str(base_path))
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e:
                print(f"Error loading base.css: {e}")
