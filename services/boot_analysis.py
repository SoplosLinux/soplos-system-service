import re
import subprocess


_TIME_RE = re.compile(r'([\d.]+)(ms|s|min|h)')


def _parse_duration_ms(text):
    """Parse a systemd-analyze duration token (e.g. '1.234s', '2min 3.4s') to ms."""
    total_ms = 0.0
    for value, unit in _TIME_RE.findall(text):
        value = float(value)
        if unit == 'ms':
            total_ms += value
        elif unit == 's':
            total_ms += value * 1000
        elif unit == 'min':
            total_ms += value * 60000
        elif unit == 'h':
            total_ms += value * 3600000
    return total_ms


def get_boot_blame(limit=15):
    """
    Return the slowest-starting *services* at boot, as [{'name', 'time_ms'}, ...].

    systemd-analyze blame also lists .device/.mount/.scope/.slice units. Those
    are not actionable (nothing to disable) and are dominated by noise: every
    machine's legacy ttyS0-ttyS3 serial ports and auto-generated
    /dev/disk/by-path/... device units show up with near-identical times that
    reflect udev probe/settle delay, not real startup cost, and their names
    carry systemd's \\xHH path escaping (unreadable in the UI). Only .service
    and .timer units are ever something the user can actually act on, so
    everything else is filtered here rather than shown as a false positive.
    """
    try:
        result = subprocess.run(
            ['systemd-analyze', 'blame', '--no-pager'],
            capture_output=True, text=True, timeout=15
        )
        entries = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            name = parts[1]
            if not (name.endswith('.service') or name.endswith('.timer')):
                continue
            time_ms = _parse_duration_ms(parts[0])
            entries.append({'name': name, 'time_ms': time_ms})
        return entries[:limit]
    except Exception as e:
        print(f"Error getting boot blame: {e}")
        return []


def get_frequent_timers(max_interval_seconds=300):
    """
    Return enabled timers that re-trigger their unit more often than
    max_interval_seconds, based on OnUnitActiveUSec/OnCalendar's effective
    interval reported by systemctl. Frequent timers keep waking an otherwise
    idle CPU, which matters for laptop battery life.
    """
    try:
        result = subprocess.run(
            ['systemctl', 'list-timers', '--all', '--no-pager', '--no-legend'],
            capture_output=True, text=True, timeout=15
        )
        timer_names = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split()
            for token in parts:
                if token.endswith('.timer'):
                    timer_names.append(token)
                    break

        frequent = []
        for timer in timer_names:
            interval_s = _get_timer_interval_seconds(timer)
            if interval_s is not None and 0 < interval_s <= max_interval_seconds:
                frequent.append({'name': timer, 'interval_seconds': interval_s})
        return frequent
    except Exception as e:
        print(f"Error getting frequent timers: {e}")
        return []


def _get_timer_interval_seconds(timer_name):
    """Read OnUnitActiveUSec for a timer unit, in seconds, or None if not set."""
    try:
        result = subprocess.run(
            ['systemctl', 'show', timer_name, '-p', 'OnUnitActiveUSec', '--value'],
            capture_output=True, text=True, timeout=10
        )
        value = result.stdout.strip()
        if not value or value == '0':
            return None
        return _parse_duration_ms(value) / 1000
    except Exception:
        return None
