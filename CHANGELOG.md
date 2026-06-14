# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/en/).

## [1.0.0-1] - 2026-06-14

### Rewritten

Complete rewrite of the application after almost a year on hold. The original skeleton has been replaced with a fully functional implementation following the Soplos application architecture pattern.

- **GTK3 interface**: Full window with sidebar navigation (Gtk.ListBox) and content switching (Gtk.Stack)
- **Services view**: Sortable and filterable TreeView with all systemd service columns, color-coded active state (green/red)
- **Details panel**: Gtk.Paned split view showing service name, state and description below the list
- **Service control**: Start, stop, restart, enable and disable buttons with confirmation dialogs
- **Log viewer**: Second navigation view with real-time journalctl output for the selected service
- **Environment detection**: Detects GNOME/XFCE/KDE desktop and X11/Wayland protocol at startup
- **CSD header bar**: Applied on GNOME, skipped on XFCE and KDE for native window decoration compatibility
- **Automatic theme detection**: Dark/light detection per desktop (xfconf-query for XFCE, kdeglobals for KDE, gsettings for GNOME)
- **CSS theming**: base.css plus dark.css or light.css loaded according to detected theme, with Soplos orange brand color
- **Modular architecture**: core/ (application, environment, theme_manager) + ui/ (main_window, services_view, logs_view) + services/ + utils/
- **Improved pkexec elevation**: Now passes XDG_CURRENT_DESKTOP, XDG_SESSION_TYPE, LANG and other environment variables through pkexec so that environment and theme detection work correctly as root
- **Threading**: Service listing and log fetching run in background threads to keep the UI responsive
- **Fixed**: Duplicate service rows — the original _populate_service_store() appended each service twice
- **Fixed**: utils/strings.py — removed the duplicate redefinition of six language dicts, the STRINGS dict and get_string() that existed after line 47, including the dead double-return on the last line
- **Fixed**: Removed debug print statements (DEBUG: Passed root check..., DEBUG: Gtk initialized..., etc.) from main.py

### Improved

- services/systemd.py: All control functions now use subprocess.run with capture_output and timeout instead of subprocess.call; added get_service_logs() using journalctl
- utils/strings.py: Added global _() function and set_language() so all modules share a single language state without passing lang everywhere
- utils/gettext/*.py: Added new string keys for all UI elements added in this release across all 8 languages

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
