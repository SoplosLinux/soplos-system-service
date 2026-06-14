# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/en/).

## [1.0.0-1] - 2026-06-14

### Rewritten

Complete rewrite of the application after almost a year on hold. The original skeleton has been replaced with a fully functional implementation following the Soplos application architecture pattern.

- **Gtk.Notebook tabs**: Two-tab interface (Services / Logs) with Soplos orange accent on the active tab, replacing the original skeleton layout
- **Services view**: Sortable TreeView with color-coded active state (green for active, red for failed/inactive) and color-coded load state (not-found in red)
- **Smart action buttons**: Start, Stop and Restart buttons enabled or disabled based on the current service state; all five controls disabled until a service is selected
- **Scrollable details panel**: Gtk.TextView inside Gtk.ScrolledWindow replacing the original Gtk.Label, preventing window deformation on long output
- **Log viewer tab**: Gtk.TextView with monospace font showing journalctl output for the selected service
- **Progress bar**: Gtk.Revealer with Gtk.ProgressBar in pulse mode shown during service listing and service operations, following the Soplos standard
- **CSD HeaderBar**: Always active regardless of desktop environment; subtitle updated with operation status (loading count, errors)
- **Soplos footer**: Static DE and display protocol on the left, base version without debian revision suffix on the right
- **Dark/light theme**: Pre-detected as the regular user before pkexec elevation and passed via SOPLOS_COLOR_SCHEME environment variable, ensuring correct colors when running as root under XFCE, KDE or GNOME
- **CSS loading**: Two separate Gtk.CssProvider instances following the Soplos theme pattern (dark.css or light.css first, then base.css), not a combined string
- **i18n**: All UI strings through the dict-based _() system; new keys added for all new UI elements across all 8 languages
- **pycache cleanup**: Automatic cleanup of __pycache__ directories on exit via atexit.register and signal.signal handlers for SIGINT and SIGTERM in main.py
- **Modular architecture**: core/ (application, environment, theme_manager) + ui/ (main_window, services_view, logs_view) + services/systemd.py + utils/strings.py + utils/gettext/
- **Improved pkexec elevation**: Forwards DISPLAY, XAUTHORITY, XDG_CURRENT_DESKTOP, XDG_SESSION_TYPE, XDG_SESSION_DESKTOP, DESKTOP_SESSION, DBUS_SESSION_BUS_ADDRESS, LANG, LANGUAGE, LC_ALL, HOME, USER, SOPLOS_SYSTEM_SERVICE_LANG and SOPLOS_COLOR_SCHEME through pkexec env

### Added

- Polkit policy file: debian/org.soplos.systemservice.policy
- Desktop launcher: debian/org.soplos.systemservice.desktop with Name and Comment in all 8 languages
- Bash launcher wrapper: debian/soplos-system-services
- Debian packaging: debian/control and debian/copyright
- Icons: 48x48, 64x64 and 128x128 subfolders under assets/icons/ from the original 1024px icon
- Screenshots: assets/screenshots/screenshot01.png, screenshot02.png, screenshot03.png

### Fixed

- Duplicate service rows in the original _populate_service_store() which appended each service twice
- Bullet character (U+25CF) parsed as service name when systemctl prefixed failed units with the symbol
- utils/strings.py: removed duplicate redefinition of all language dicts and dead double-return after line 47
- Removed all debug print statements from main.py (DEBUG: Passed root check, DEBUG: Gtk initialized, etc.)
- Progress bar position: was appearing below the footer due to pack_end ordering; footer is now packed first so the progress bar sits correctly between content and footer
- Progress bar visibility: added 700ms minimum display time so the bar is noticeable even when service listing completes instantly
- GTK_IM_MODULE set to gtk-im-context-simple before pkexec to suppress ibus connection warnings when running as root

### Improved

- services/systemd.py: All control functions use subprocess.run with capture_output and timeout; added get_service_logs() via journalctl
- utils/strings.py: Added global _() and set_language() and get_current_language() so all modules share a single language state

## [1.0.0] - 2025-07-31

### Added

- Initial project creation with GTK3 application skeleton
- systemd service listing via systemctl list-units
- Basic service control functions: start, stop, restart, enable, disable
- 8-language string system with dict-based translations (es, en, fr, pt, de, it, ro, ru)
- pkexec privilege elevation in main.py
- Basic TreeView layout for the service list

---

## Types of Changes

- **Added** for new features
- **Rewritten** for complete rewrites of existing modules
- **Improved** for changes in existing functionality
- **Fixed** for bug fixes

## Author

Developed and maintained by Sergi Perich
Website: https://soplos.org
Contact: info@soploslinux.com

## Support

- Documentation: https://soplos.org
- Community: https://soplos.org/forums/
- Issues: https://github.com/SoplosLinux/soplos-system-service/issues
