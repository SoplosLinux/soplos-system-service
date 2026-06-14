import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango

from utils.strings import _
from services.systemd import (
    list_services, get_service_status,
    start_service, stop_service, restart_service,
    enable_service, disable_service,
)


class ServicesView(Gtk.Box):

    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._main_window = main_window
        self._selected_service = None
        self._selected_active = None
        self._build_ui()
        # Defer initial load so the parent window is fully built first
        GLib.idle_add(self._load_services)

    def _build_ui(self):
        # Top: paned split — service list on top, details on bottom
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_position(350)
        self.pack_start(paned, True, True, 0)

        # Upper pane: sortable TreeView
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # name, loaded, active, sub, description
        self._store = Gtk.ListStore(str, str, str, str, str)
        self._treeview = Gtk.TreeView(model=self._store)
        self._treeview.set_headers_clickable(True)
        self._treeview.set_rules_hint(True)

        col_defs = [
            (_('table.name'), 0, 260),
            (_('table.loaded'), 1, 90),
            (_('table.active'), 2, 90),
            (_('table.sub'), 3, 90),
            (_('table.description'), 4, -1),
        ]
        for title, col_id, width in col_defs:
            renderer = Gtk.CellRendererText()
            renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
            col = Gtk.TreeViewColumn(title, renderer, text=col_id)
            col.set_sort_column_id(col_id)
            col.set_resizable(True)
            if width > 0:
                col.set_fixed_width(width)
                col.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            else:
                col.set_expand(True)
            if col_id == 1:
                col.set_cell_data_func(renderer, self._cell_color_loaded)
            if col_id == 2:
                col.set_cell_data_func(renderer, self._cell_color_active)
            self._treeview.append_column(col)

        self._treeview.get_selection().connect('changed', self._on_selection_changed)
        scrolled.add(self._treeview)
        paned.pack1(scrolled, True, False)

        # Lower pane: scrollable details panel
        details_scroll = Gtk.ScrolledWindow()
        details_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        details_scroll.set_shadow_type(Gtk.ShadowType.NONE)
        details_scroll.get_style_context().add_class('soplos-card')

        self._details_buffer = Gtk.TextBuffer()
        self._details_buffer.set_text(_('details.no_selection'))
        self._details_view = Gtk.TextView(buffer=self._details_buffer)
        self._details_view.set_editable(False)
        self._details_view.set_cursor_visible(False)
        self._details_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._details_view.set_monospace(True)
        self._details_view.set_left_margin(10)
        self._details_view.set_right_margin(10)
        self._details_view.set_top_margin(8)
        self._details_view.set_bottom_margin(8)
        details_scroll.add(self._details_view)

        paned.pack2(details_scroll, False, False)

        # Bottom toolbar: control buttons
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_border_width(8)

        # (key, handler, attr_name)
        btn_defs = [
            ('btn.start',   self._on_start,   '_btn_start'),
            ('btn.stop',    self._on_stop,    '_btn_stop'),
            ('btn.restart', self._on_restart, '_btn_restart'),
            ('btn.enable',  self._on_enable,  '_btn_enable'),
            ('btn.disable', self._on_disable, '_btn_disable'),
        ]
        self._ctrl_buttons = []
        for key, handler, attr in btn_defs:
            btn = Gtk.Button(label=_(key))
            btn.set_sensitive(False)
            btn.connect('clicked', handler)
            toolbar.pack_start(btn, False, False, 0)
            self._ctrl_buttons.append(btn)
            setattr(self, attr, btn)

        # Refresh button on the right
        btn_refresh = Gtk.Button(label=_('btn.refresh'))
        btn_refresh.connect('clicked', lambda _b: self._load_services())
        toolbar.pack_end(btn_refresh, False, False, 0)

        self.pack_end(toolbar, False, False, 0)

    def _cell_color_loaded(self, column, renderer, model, tree_iter, data):
        value = model.get_value(tree_iter, 1).lower()
        if value == 'not-found':
            renderer.set_property('foreground', '#e74c3c')
            renderer.set_property('foreground-set', True)
        elif value == 'loaded':
            renderer.set_property('foreground-set', False)
        else:
            renderer.set_property('foreground-set', False)

    def _cell_color_active(self, column, renderer, model, tree_iter, data):
        value = model.get_value(tree_iter, 2).lower()
        if value == 'active':
            renderer.set_property('foreground', '#4ec94e')
            renderer.set_property('foreground-set', True)
        elif value in ('failed', 'inactive'):
            renderer.set_property('foreground', '#e74c3c')
            renderer.set_property('foreground-set', True)
        else:
            renderer.set_property('foreground-set', False)

    def _load_services(self):
        self._main_window.show_progress(_('status.loading'))
        self._store.clear()
        threading.Thread(target=self._fetch_services, daemon=True).start()
        return False

    def _fetch_services(self):
        services = list_services()
        GLib.idle_add(self._populate, services)

    def _populate(self, services):
        self._store.clear()
        for svc in services:
            self._store.append([
                svc['name'],
                svc['loaded'],
                svc['active'],
                svc['sub'],
                svc['description'],
            ])
        count = len(services)
        # Keep the progress bar visible for a minimum time so it is noticeable.
        GLib.timeout_add(700, self._finish_loading, count)
        return False

    def _finish_loading(self, count):
        self._main_window.hide_progress()
        self._main_window.set_status(f'{count} services')
        return False

    def _on_selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        if tree_iter is None:
            self._selected_service = None
            self._selected_active = None
            self._details_buffer.set_text(_('details.no_selection'))
            for btn in self._ctrl_buttons:
                btn.set_sensitive(False)
            self._main_window.on_service_selected(None)
            return

        row = model[tree_iter]
        name = row[0]
        active = row[2].lower()
        self._selected_service = name
        self._selected_active = active

        self._update_button_states(active)
        threading.Thread(target=self._fetch_details, args=(name,), daemon=True).start()
        self._main_window.on_service_selected(name)

    def _update_button_states(self, active):
        is_running = active == 'active'
        is_failed  = active == 'failed'
        # Start: only when not already running
        self._btn_start.set_sensitive(not is_running)
        # Stop/Restart: only when running or failed
        self._btn_stop.set_sensitive(is_running or is_failed)
        self._btn_restart.set_sensitive(is_running or is_failed)
        # Enable/Disable: always available when something is selected
        self._btn_enable.set_sensitive(True)
        self._btn_disable.set_sensitive(True)

    def _fetch_details(self, name):
        status = get_service_status(name)
        GLib.idle_add(self._show_details, status)

    def _show_details(self, text):
        self._details_buffer.set_text(text)
        return False

    def _confirm(self, key, name):
        msg = _(key).format(name=name)
        dialog = Gtk.MessageDialog(
            transient_for=self._main_window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_('confirm.title'),
        )
        dialog.format_secondary_text(msg)
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def _run_action(self, fn, confirm_key):
        if not self._selected_service:
            return
        name = self._selected_service
        if not self._confirm(confirm_key, name):
            return
        self._main_window.show_progress(_('status.loading'))
        ok, err = fn(name)
        if not ok:
            self._main_window.hide_progress()
            d = Gtk.MessageDialog(
                transient_for=self._main_window,
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_('status.error'),
            )
            d.format_secondary_text(err or '')
            d.run()
            d.destroy()
        self._load_services()

    def _on_start(self, _btn):
        self._run_action(start_service, 'confirm.start')

    def _on_stop(self, _btn):
        self._run_action(stop_service, 'confirm.stop')

    def _on_restart(self, _btn):
        self._run_action(restart_service, 'confirm.restart')

    def _on_enable(self, _btn):
        self._run_action(enable_service, 'confirm.enable')

    def _on_disable(self, _btn):
        self._run_action(disable_service, 'confirm.disable')
