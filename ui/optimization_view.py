import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango

from utils.strings import _
from services.systemd import (
    list_services, disable_service, stop_service,
    enable_service, start_service,
)
from services.orphans import remove_dangling_symlinks
from core.optimization_rules import evaluate_rules

_CATEGORY_KEYS = {
    'hardware': 'opt.category.hardware',
    'redundant': 'opt.category.redundant',
    'orphan': 'opt.category.orphan',
    'maintenance': 'opt.category.maintenance',
    'boot_block': 'opt.category.boot_block',
}
_RESOURCE_KEYS = {
    'ram': 'opt.resource.ram',
    'boot': 'opt.resource.boot',
    'power': 'opt.resource.power',
    'disk': 'opt.resource.disk',
    'cleanup': 'opt.resource.cleanup',
}
_RISK_KEYS = {
    'low': 'opt.risk.low',
    'medium': 'opt.risk.medium',
}


class OptimizationView(Gtk.Box):

    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._main_window = main_window
        self._suggestions = []
        self._build_ui()
        GLib.idle_add(self._run_scan)

    def _build_ui(self):
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_position(380)
        self.pack_start(paned, True, True, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # apply?, service, category, resource, reason, risk
        self._store = Gtk.ListStore(bool, str, str, str, str, str)
        self._treeview = Gtk.TreeView(model=self._store)
        self._treeview.set_rules_hint(True)

        toggle = Gtk.CellRendererToggle()
        toggle.connect('toggled', self._on_toggle)
        col_toggle = Gtk.TreeViewColumn('', toggle, active=0)
        self._treeview.append_column(col_toggle)

        # Full, non-truncated reason text (e.g. the exact symlink path being
        # removed) on hover, since the column itself ellipsizes long values.
        self._treeview.set_tooltip_column(4)

        text_cols = [
            (_('opt.column.service'), 1, 220),
            (_('opt.column.category'), 2, 140),
            (_('opt.column.resource'), 3, 90),
            (_('opt.column.reason'), 4, -1),
            (_('opt.column.risk'), 5, 80),
        ]
        for title, col_id, width in text_cols:
            renderer = Gtk.CellRendererText()
            renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
            col = Gtk.TreeViewColumn(title, renderer, text=col_id)
            col.set_resizable(True)
            if width > 0:
                col.set_fixed_width(width)
                col.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            else:
                col.set_expand(True)
            self._treeview.append_column(col)

        scrolled.add(self._treeview)
        paned.pack1(scrolled, True, False)

        # Lower pane: informative boot/power findings
        info_scroll = Gtk.ScrolledWindow()
        info_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        info_scroll.get_style_context().add_class('soplos-card')

        self._info_buffer = Gtk.TextBuffer()
        self._info_view = Gtk.TextView(buffer=self._info_buffer)
        self._info_view.set_editable(False)
        self._info_view.set_cursor_visible(False)
        self._info_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._info_view.set_left_margin(10)
        self._info_view.set_right_margin(10)
        self._info_view.set_top_margin(8)
        self._info_view.set_bottom_margin(8)
        info_scroll.add(self._info_view)
        paned.pack2(info_scroll, False, False)

        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_border_width(8)

        self._select_all_check = Gtk.ToggleButton(label=_('opt.btn.select_all'))
        self._select_all_check.connect('toggled', self._on_select_all_toggled)
        toolbar.pack_start(self._select_all_check, False, False, 0)

        self._btn_apply = Gtk.Button(label=_('opt.btn.apply'))
        self._btn_apply.set_sensitive(False)
        self._btn_apply.connect('clicked', self._on_apply)
        toolbar.pack_start(self._btn_apply, False, False, 0)

        btn_scan = Gtk.Button(label=_('opt.btn.scan'))
        btn_scan.connect('clicked', lambda _b: self._run_scan())
        toolbar.pack_end(btn_scan, False, False, 0)

        self.pack_end(toolbar, False, False, 0)

    def _on_toggle(self, _renderer, path):
        row = self._store[path]
        row[0] = not row[0]
        self._sync_select_all_check()
        self._update_apply_sensitivity()

    def _on_select_all_toggled(self, checkbutton):
        active = checkbutton.get_active()
        for row in self._store:
            row[0] = active
        self._update_apply_sensitivity()

    def _sync_select_all_check(self):
        rows = list(self._store)
        all_checked = bool(rows) and all(row[0] for row in rows)
        self._select_all_check.handler_block_by_func(self._on_select_all_toggled)
        self._select_all_check.set_active(all_checked)
        self._select_all_check.handler_unblock_by_func(self._on_select_all_toggled)

    def _update_apply_sensitivity(self):
        any_checked = any(row[0] for row in self._store)
        self._btn_apply.set_sensitive(any_checked)

    def _run_scan(self):
        self._main_window.show_progress(_('opt.status.scanning'))
        self._store.clear()
        self._info_buffer.set_text('')
        self._select_all_check.handler_block_by_func(self._on_select_all_toggled)
        self._select_all_check.set_active(False)
        self._select_all_check.handler_unblock_by_func(self._on_select_all_toggled)
        self._btn_apply.set_sensitive(False)
        threading.Thread(target=self._scan_thread, daemon=True).start()
        return False

    def _scan_thread(self):
        services = list_services()
        actionable, informative = evaluate_rules(services)
        GLib.idle_add(self._populate, actionable, informative)

    def _populate(self, actionable, informative):
        self._suggestions = actionable
        self._store.clear()
        for item in actionable:
            category_label = _(_CATEGORY_KEYS.get(item['category'], item['category']))
            resource_label = _(_RESOURCE_KEYS.get(item['resource'], item['resource']))
            risk_label = _(_RISK_KEYS.get(item['risk'], item['risk']))
            reason_text = _(item['reason_key']).format(**item['reason_args'])
            self._store.append([
                False, item['service'], category_label, resource_label,
                reason_text, risk_label,
            ])

        if informative:
            lines = []
            for entry in informative:
                if entry['category'] == 'boot':
                    lines.append(f"{entry['service']}: {entry['detail']:.0f} ms")
                else:
                    lines.append(f"{entry['service']}: ~{entry['detail']:.0f}s")
            self._info_buffer.set_text('\n'.join(lines))
        else:
            self._info_buffer.set_text(_('opt.status.none_found'))

        self._main_window.hide_progress()
        count = len(actionable)
        self._main_window.set_status(f'{count} suggestions')
        return False

    def _on_apply(self, _btn):
        selected = [row[1] for row in self._store if row[0]]
        if not selected:
            return

        by_name = {item['service']: item for item in self._suggestions}
        items = [by_name[name] for name in selected if name in by_name]

        counts = {}
        for item in items:
            action = item.get('action', 'disable')
            counts[action] = counts.get(action, 0) + 1

        lines = [_('opt.confirm.header')]
        if counts.get('disable'):
            lines.append(_('opt.confirm.summary_disable').format(count=counts['disable']))
        if counts.get('enable'):
            lines.append(_('opt.confirm.summary_enable').format(count=counts['enable']))
        if counts.get('remove_symlink'):
            lines.append(_('opt.confirm.summary_remove').format(count=counts['remove_symlink']))

        dialog = Gtk.MessageDialog(
            transient_for=self._main_window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_('confirm.title'),
        )
        dialog.format_secondary_text('\n'.join(lines))
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.YES:
            return

        self._main_window.show_progress(_('opt.status.applying'))
        threading.Thread(target=self._apply_thread, args=(items,), daemon=True).start()

    def _apply_thread(self, items):
        for item in items:
            name = item['service']
            action = item.get('action', 'disable')
            if action == 'enable':
                enable_service(name)
                start_service(name)
            elif action == 'remove_symlink':
                remove_dangling_symlinks(item.get('symlink_paths', []))
            else:
                stop_service(name)
                disable_service(name)
        GLib.idle_add(self._run_scan)
