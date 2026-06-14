import os
import subprocess


class EnvironmentDetector:

    def __init__(self):
        self._cached = None

    def detect_all(self):
        if self._cached:
            return self._cached
        self._cached = {
            'desktop_environment': self._detect_desktop(),
            'display_protocol': self._detect_protocol(),
            'theme_type': self._detect_theme(),
        }
        return self._cached

    @property
    def is_dark_theme(self):
        return self.detect_all()['theme_type'] == 'dark'

    def _detect_desktop(self):
        for env_var in ('XDG_CURRENT_DESKTOP', 'DESKTOP_SESSION', 'XDG_SESSION_DESKTOP'):
            val = os.environ.get(env_var, '').lower()
            if 'xfce' in val:
                return 'xfce'
            if 'kde' in val or 'plasma' in val:
                return 'kde'
            if 'gnome' in val:
                return 'gnome'
        return 'unknown'

    def _detect_protocol(self):
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        if 'wayland' in session_type:
            return 'wayland'
        if 'x11' in session_type or os.environ.get('DISPLAY'):
            return 'x11'
        return 'unknown'

    def _detect_theme(self):
        # When running as root via pkexec, the launcher pre-detects the theme
        # as the regular user and passes it through this env var.
        forced = os.environ.get('SOPLOS_COLOR_SCHEME', '').lower()
        if forced in ('dark', 'light'):
            return forced

        desktop = self._detect_desktop()
        if desktop == 'xfce':
            return self._detect_xfce_theme()
        if desktop == 'kde':
            return self._detect_kde_theme()
        return self._detect_gnome_theme()

    def _detect_xfce_theme(self):
        try:
            result = subprocess.run(
                ['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'],
                capture_output=True, text=True, timeout=2
            )
            if 'dark' in result.stdout.lower():
                return 'dark'
            return 'light'
        except Exception:
            return self._detect_gnome_theme()

    def _detect_kde_theme(self):
        try:
            kdeglobals = os.path.expanduser('~/.config/kdeglobals')
            if os.path.exists(kdeglobals):
                with open(kdeglobals, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if 'dark' in content or 'breeze-dark' in content:
                        return 'dark'
            return 'light'
        except Exception:
            return self._detect_gnome_theme()

    def _detect_gnome_theme(self):
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True, text=True, timeout=2
            )
            if 'dark' in result.stdout.lower():
                return 'dark'
            result2 = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                capture_output=True, text=True, timeout=2
            )
            if 'dark' in result2.stdout.lower():
                return 'dark'
        except Exception:
            pass
        settings_dark = False
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            settings = Gtk.Settings.get_default()
            if settings:
                settings_dark = settings.get_property('gtk-application-prefer-dark-theme')
                if not settings_dark:
                    theme_name = settings.get_property('gtk-theme-name') or ''
                    settings_dark = 'dark' in theme_name.lower()
        except Exception:
            pass
        return 'dark' if settings_dark else 'light'


_instance = None


def get_environment_detector():
    global _instance
    if _instance is None:
        _instance = EnvironmentDetector()
    return _instance
