import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango

from utils.strings import _
from services.systemd import get_service_logs


class LogsView(Gtk.Box):

    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._main_window = main_window
        self._current_service = None
        self._build_ui()

    def _build_ui(self):
        # Placeholder label shown when no service is selected
        self._placeholder = Gtk.Label(label=_('logs.select_service'))
        self._placeholder.set_halign(Gtk.Align.CENTER)
        self._placeholder.set_valign(Gtk.Align.CENTER)
        self._placeholder.get_style_context().add_class('dim-label')

        # Scrolled text view for log output
        self._scrolled = Gtk.ScrolledWindow()
        self._scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self._textview = Gtk.TextView()
        self._textview.set_editable(False)
        self._textview.set_cursor_visible(False)
        self._textview.set_monospace(True)
        self._textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._buffer = self._textview.get_buffer()
        self._scrolled.add(self._textview)

        # Stack to switch between placeholder and log view
        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._stack.add_named(self._placeholder, 'placeholder')
        self._stack.add_named(self._scrolled, 'logs')
        self.pack_start(self._stack, True, True, 0)

        # Bottom toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_border_width(8)

        self._service_label = Gtk.Label(label='')
        self._service_label.set_halign(Gtk.Align.START)
        self._service_label.get_style_context().add_class('dim-label')
        toolbar.pack_start(self._service_label, True, True, 0)

        btn_refresh = Gtk.Button(label=_('btn.refresh'))
        btn_refresh.connect('clicked', lambda _b: self._load_logs())
        toolbar.pack_end(btn_refresh, False, False, 0)

        self.pack_end(toolbar, False, False, 0)

    def set_service(self, service_name):
        self._current_service = service_name
        if service_name:
            self._service_label.set_text(service_name)
            self._load_logs()
        else:
            self._service_label.set_text('')
            self._buffer.set_text('')
            self._stack.set_visible_child_name('placeholder')

    def _load_logs(self):
        if not self._current_service:
            return
        self._buffer.set_text(_('status.loading'))
        self._stack.set_visible_child_name('logs')
        threading.Thread(
            target=self._fetch_logs,
            args=(self._current_service,),
            daemon=True
        ).start()

    def _fetch_logs(self, service_name):
        logs = get_service_logs(service_name)
        GLib.idle_add(self._show_logs, logs)

    def _show_logs(self, text):
        self._buffer.set_text(text or _('logs.no_logs'))
        # Scroll to the end
        end_iter = self._buffer.get_end_iter()
        self._textview.scroll_to_iter(end_iter, 0.0, False, 0.0, 1.0)
        return False
