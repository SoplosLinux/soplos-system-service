import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os
import sys
from utils.strings import get_string, get_system_language

APP_NAME = "soplos-system-services"

def relaunch_as_root():
    """Relaunch the program with pkexec if not running as root."""
    if os.geteuid() != 0:
        try:
            script = os.path.abspath(sys.argv[0])
            display = os.environ.get("DISPLAY")
            xauthority = os.environ.get("XAUTHORITY")
            env = os.environ.copy()
            if display:
                env["DISPLAY"] = display
            if xauthority:
                env["XAUTHORITY"] = xauthority
            args = ["pkexec", "env"]
            if display:
                args += [f"DISPLAY={display}"]
            if xauthority:
                args += [f"XAUTHORITY={xauthority}"]
            args += [sys.executable, script] + sys.argv[1:]
            os.execvpe("pkexec", args, env)
        except Exception as e:
            dialog = Gtk.MessageDialog(
                parent=None,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE,
                text="This program must be run as administrator (pkexec)."
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
            sys.exit(1)

# Import the main window from the UI module (future modularization)
try:
    from ui.main_window import MainWindow
except ImportError:
    class MainWindow(Gtk.Window):
        def __init__(self):
            Gtk.Window.__init__(self, title="Soplos System Services")
            self.set_default_size(950, 650)
            self.set_border_width(0)
            # Here will go the sidebar, service list, details panel, etc.
            # The design and style will follow the Soplos Welcome pattern.
            # ...professional structure, ready for tabs and widgets...

def main():
    relaunch_as_root()
    print("DEBUG: Passed root check, initializing Gtk...")
    # Check if Gtk can be initialized (for headless or broken DISPLAY)
    if not Gtk.init_check()[0]:
        print("Error: Gtk could not be initialized. Make sure you are running in a graphical environment (X11 or Wayland).")
        sys.exit(2)
    print("DEBUG: Gtk initialized, creating MainWindow...")
    lang = get_system_language()
    win = MainWindow(lang=lang)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    print("DEBUG: MainWindow shown, entering Gtk.main() loop.")
    Gtk.main()

if __name__ == "__main__":
    main()
