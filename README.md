# Soplos System Services

[![License: GPL-3.0+](https://img.shields.io/badge/License-GPL--3.0%2B-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-1.0.0--1-green.svg)]()

GTK3 graphical manager for systemd services on Soplos Linux.

*Gestor gráfico GTK3 para servicios systemd en Soplos Linux.*

*Gestionnaire graphique GTK3 pour les services systemd sous Soplos Linux.*

*GTK3-Verwaltungsoberfläche für systemd-Dienste unter Soplos Linux.*

*Gestore grafico GTK3 per i servizi systemd su Soplos Linux.*

*Gestor gráfico GTK3 para serviços systemd no Soplos Linux.*

*Manager grafic GTK3 pentru serviciile systemd pe Soplos Linux.*

*Графический менеджер GTK3 для служб systemd в Soplos Linux.*

## Description

Soplos System Services is a graphical tool for managing systemd services on Soplos Linux Boro, Tyron and Tyson. It provides a clean interface to view, control and monitor all system services without using the terminal. Supports all major desktop environments and display protocols with complete internationalization for 8 languages.

## Features

- **Service list**: Complete view of all systemd services with name, load state, active state, sub-state and description
- **Service control**: Start, stop, restart, enable and disable services with confirmation dialogs
- **Service details**: Dedicated details panel showing the state of the selected service
- **Log viewer**: Real-time journalctl log output for any selected service
- **Desktop integration**: GNOME, XFCE and KDE (Plasma) support, with CSD header bar on GNOME
- **Display protocol**: Compatible with X11 and Wayland
- **Theme detection**: Automatic dark/light theme detection per desktop environment
- **CSS theming**: Consistent Soplos visual style applied via GTK3 CSS
- **8-language interface**: Spanish, English, French, German, Italian, Portuguese, Romanian, Russian
- **Privilege elevation**: Transparent root access via pkexec

## Installation

```bash
sudo apt install soplos-system-services
```

Or from source:

```bash
git clone https://github.com/SoplosLinux/soplos-system-service
cd soplos-system-service
sudo python3 setup.py install
```

## Supported Languages

- Spanish (Espanol)
- English
- French (Francais)
- German (Deutsch)
- Italian (Italiano)
- Portuguese (Portugues)
- Romanian (Romana)
- Russian (Russkiy)

## Requirements

- Python 3.7 or later
- PyGObject (python3-gi)
- GTK 3.0 (gir1.2-gtk-3.0)
- systemd
- pkexec (PolicyKit)

## License

This project is licensed under [GPL-3.0+](https://www.gnu.org/licenses/gpl-3.0.html) (GNU General Public License version 3 or later).

Any derivative work must be distributed under the same license (GPL-3.0+).

For more details, see the LICENSE file or visit [gnu.org/licenses/gpl-3.0](https://www.gnu.org/licenses/gpl-3.0.html).

## Developer

Developed by Sergi Perich
Website: https://soplos.org
Contact: info@soploslinux.com

## Links

- [Website](https://soplos.org)
- [Report issues](https://github.com/SoplosLinux/soplos-system-service/issues)

## Versions

### v1.0.0-1 (14/06/2026)

Complete rewrite of the application:
- Full GTK3 interface with sidebar navigation and Gtk.Stack
- Services view with sortable and filterable TreeView
- Service details panel with start/stop/restart/enable/disable controls
- Log viewer with journalctl integration
- Environment detection (GNOME/XFCE/KDE, X11/Wayland)
- Automatic dark/light theme detection per desktop environment
- CSS theming with base/dark/light themes
- Modular architecture following the Soplos application pattern (core/ui/services/utils)
- Fixed duplicate service rendering bug in the original code
- Fixed duplicate string definitions and dead code in utils/strings.py
- Removed debug print statements from the original code

### v1.0.0 (31/07/2025)

- Initial project creation with base GTK3 structure
- systemd service listing via systemctl
- Basic service control functions (start, stop, restart, enable, disable)
- 8-language string system (es, en, fr, pt, de, it, ro, ru)
