import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from pathlib import Path

from core import APP_VERSION
from utils.strings import _
from ui.services_view import ServicesView
from ui.logs_view import LogsView


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app, env_detector):
        super().__init__(application=app)
        self._env_detector = env_detector
        self._base_dir = Path(__file__).parent.parent
        self._services_view = None
        self._logs_view = None
        self._pulse_timeout = None

        self.set_title(_('main.title'))
        self.set_default_size(1000, 680)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.get_style_context().add_class('soplos-window')

        self._set_window_icon()

        env = env_detector.detect_all()

        self._setup_headerbar()
        self._build_ui(env)
        self.connect('key-press-event', self._on_key_press)
        self.show_all()
        self.progress_revealer.set_reveal_child(False)

    def _set_window_icon(self):
        # Prefer the dot-convention name; fall back to the original hyphenated file
        for name in ('org.soplos.systemservice.png', 'org.soplos-systemservice.png'):
            icon_path = self._base_dir / 'assets' / 'icons' / name
            if icon_path.exists():
                self.set_icon_from_file(str(icon_path))
                return
        self.set_icon_name('preferences-system')

    def _setup_headerbar(self):
        self._header = Gtk.HeaderBar()
        self._header.set_show_close_button(True)
        self._header.set_title(_('main.title'))
        self._header.set_decoration_layout('menu:minimize,maximize,close')
        self.set_titlebar(self._header)

    def _build_ui(self, env):
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Notebook with two tabs
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        notebook.set_scrollable(False)
        notebook.set_show_border(False)
        self._apply_notebook_css()

        self._services_view = ServicesView(self)
        tab_services = self._make_tab_label('preferences-system', _('tab.services'))
        notebook.append_page(self._services_view, tab_services)

        self._logs_view = LogsView(self)
        tab_logs = self._make_tab_label('text-x-log', _('tab.logs'))
        notebook.append_page(self._logs_view, tab_logs)

        main_vbox.pack_start(notebook, True, True, 0)

        # Footer must be packed_end first so it ends up at the very bottom.
        # Progress bar is packed_end second so it sits between content and footer.
        self._build_footer(main_vbox, env)
        self._build_progress_bar(main_vbox)

    def _build_progress_bar(self, vbox):
        self.progress_revealer = Gtk.Revealer()
        self.progress_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)

        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        progress_box.set_margin_start(15)
        progress_box.set_margin_end(15)
        progress_box.set_margin_top(6)
        progress_box.set_margin_bottom(4)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        progress_box.pack_start(self.progress_bar, False, False, 0)

        self.progress_revealer.add(progress_box)
        vbox.pack_end(self.progress_revealer, False, False, 0)

    def show_progress(self, message):
        if self._pulse_timeout:
            GLib.source_remove(self._pulse_timeout)
            self._pulse_timeout = None
        self.progress_bar.set_text(message)
        self.progress_bar.set_fraction(0.0)
        self.progress_revealer.set_reveal_child(True)
        self._pulse_timeout = GLib.timeout_add(120, self._do_pulse)

    def hide_progress(self):
        if self._pulse_timeout:
            GLib.source_remove(self._pulse_timeout)
            self._pulse_timeout = None
        self.progress_revealer.set_reveal_child(False)
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_text('')

    def _do_pulse(self):
        self.progress_bar.pulse()
        return True

    def _apply_notebook_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            notebook > header {
                min-height: 20px;
                padding: 0;
            }
            notebook > header > tabs > tab {
                min-height: 20px;
                padding: 8px 16px;
            }
            notebook > header > tabs > tab label {
                padding: 2px 6px;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _make_tab_label(self, icon_name, text):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        label = Gtk.Label(label=text)
        box.pack_start(icon, False, False, 0)
        box.pack_start(label, False, False, 0)
        box.show_all()
        return box

    def _build_footer(self, vbox, env):
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.set_margin_start(15)
        footer.set_margin_end(15)
        footer.set_margin_top(6)
        footer.set_margin_bottom(6)
        footer.get_style_context().add_class('soplos-footer')

        desktop = env['desktop_environment'].upper()
        protocol = env['display_protocol'].upper()

        de_label = Gtk.Label(label=f'{desktop}  ·  {protocol}')
        de_label.set_halign(Gtk.Align.START)
        de_label.get_style_context().add_class('dim-label')
        footer.pack_start(de_label, True, True, 0)

        # Show only the base version, not the debian revision suffix
        base_version = APP_VERSION.split('-')[0]
        version_label = Gtk.Label(label=f'v{base_version}')
        version_label.set_halign(Gtk.Align.END)
        version_label.get_style_context().add_class('dim-label')
        footer.pack_end(version_label, False, False, 0)

        vbox.pack_end(footer, False, False, 0)

    def set_status(self, message):
        self._header.set_subtitle(message)

    def on_service_selected(self, service_name):
        if self._logs_view:
            self._logs_view.set_service(service_name)

    def _on_key_press(self, _widget, event):
        if event.keyval == Gdk.KEY_F1:
            self._show_about()
            return True
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval in (Gdk.KEY_q, Gdk.KEY_w, Gdk.KEY_Q, Gdk.KEY_W):
                self.get_application().quit()
                return True
        return False

    def _show_about(self):
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self)
        dialog.set_modal(True)
        dialog.set_program_name(_('main.title'))
        dialog.set_version(APP_VERSION)
        dialog.set_comments(_('about.comments'))
        dialog.set_copyright('Copyright 2025-2026 Sergi Perich')
        dialog.set_license_type(Gtk.License.GPL_3_0)
        dialog.set_website('https://soplos.org')
        dialog.set_website_label('soplos.org')
        dialog.set_authors(['Sergi Perich <info@soploslinux.com>'])

        for name in ('org.soplos.systemservice.png', 'org.soplos-systemservice.png'):
            icon_path = self._base_dir / 'assets' / 'icons' / name
            if icon_path.exists():
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        str(icon_path), 96, 96, True)
                    dialog.set_logo(pixbuf)
                except Exception:
                    pass
                break

        dialog.run()
        dialog.destroy()
