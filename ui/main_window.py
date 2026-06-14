import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from services.systemd import list_services
from utils.strings import get_string  # Absolute import, works if 'config' is in PYTHONPATH

class MainWindow(Gtk.Window):
    def __init__(self, lang="en"):
        Gtk.Window.__init__(self, title=get_string(lang, "main.title"))
        self.set_default_size(950, 650)
        self.set_border_width(0)

        # Main container: horizontal box (sidebar + central panel)
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(main_box)

        # Sidebar (navigation)
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar.set_size_request(180, -1)
        sidebar.set_border_width(10)
        main_box.pack_start(sidebar, False, False, 0)

        # Sidebar navigation buttons (visual only)
        btn_services = Gtk.Button(label=get_string(lang, "sidebar.services"))
        btn_services.set_halign(Gtk.Align.FILL)
        btn_services.set_valign(Gtk.Align.START)
        sidebar.pack_start(btn_services, False, False, 0)

        btn_units = Gtk.Button(label=get_string(lang, "sidebar.units"))
        btn_units.set_halign(Gtk.Align.FILL)
        btn_units.set_valign(Gtk.Align.START)
        sidebar.pack_start(btn_units, False, False, 0)

        btn_logs = Gtk.Button(label=get_string(lang, "sidebar.logs"))
        btn_logs.set_halign(Gtk.Align.FILL)
        btn_logs.set_valign(Gtk.Align.START)
        sidebar.pack_start(btn_logs, False, False, 0)

        sidebar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 10)

        btn_about = Gtk.Button(label=get_string(lang, "sidebar.about"))
        btn_about.set_halign(Gtk.Align.FILL)
        btn_about.set_valign(Gtk.Align.END)
        sidebar.pack_end(btn_about, False, False, 0)

        # Central panel (for tabs and content)
        central_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        central_box.set_border_width(10)
        main_box.pack_start(central_box, True, True, 0)

        # Title
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='large' weight='bold'>{get_string(lang, 'main.title')}</span>")
        title_label.set_halign(Gtk.Align.START)
        central_box.pack_start(title_label, False, False, 5)

        # Placeholder for future tabs/content
        placeholder = Gtk.Label(label=get_string(lang, "main.placeholder"))
        placeholder.set_halign(Gtk.Align.CENTER)
        placeholder.set_valign(Gtk.Align.CENTER)
        central_box.pack_start(placeholder, True, True, 0)

        # Service list (TreeView)
        self.service_store = Gtk.ListStore(str, str, str, str, str)
        self._populate_service_store()
        treeview = Gtk.TreeView(model=self.service_store)

        columns = [
            (get_string(lang, "table.name"), 0),
            (get_string(lang, "table.loaded"), 1),
            (get_string(lang, "table.active"), 2),
            (get_string(lang, "table.sub"), 3),
            (get_string(lang, "table.description"), 4)
        ]
        for col_title, col_id in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=col_id)
            treeview.append_column(column)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(treeview)
        central_box.pack_start(scrolled, True, True, 0)

    def _populate_service_store(self):
        self.service_store.clear()
        for svc in list_services():
            self.service_store.append([
                svc["name"],
                svc["loaded"],
                svc["active"],
                svc["sub"],
                svc["description"]
            ])
            self.service_store.append([
                svc["name"],
                svc["loaded"],
                svc["active"],
                svc["sub"],
                svc["description"]
            ])
