import subprocess

from services.hardware import (
    detect_virtualization, has_bluetooth_adapter,
    has_wifi_adapter, has_ssd_or_nvme,
)
from services.orphans import find_orphan_services, find_dangling_symlinks
from services.boot_analysis import get_boot_blame, get_frequent_timers

# Known service names per hardware category. Only ones actually present on
# this machine (matched against the live systemctl listing) are ever
# suggested — the list below is just "what to look for", not an assumption
# that any of it is installed.
VM_GUEST_SERVICES = [
    'open-vm-tools.service', 'open-vm-tools-desktop.service',
    'qemu-guest-agent.service', 'spice-vdagentd.service',
    'spice-vdagent.service', 'spice-webdavd.service',
    'hv-fcopy-daemon.service', 'hv-kvp-daemon.service', 'hv-vss-daemon.service',
    'vboxadd.service', 'vboxadd-service.service',
]
BLUETOOTH_SERVICES = ['bluetooth.service']
WIFI_SERVICES = ['wpa_supplicant.service']
AUDIO_REDUNDANT_SERVICES = ['pulseaudio.service']

FSTRIM_TIMER = 'fstrim.timer'
NETWORK_WAIT_ONLINE_SERVICE = 'NetworkManager-wait-online.service'

BOOT_BLAME_THRESHOLD_MS = 3000
FREQUENT_TIMER_THRESHOLD_S = 300


def _is_enabled(unit_name):
    try:
        result = subprocess.run(
            ['systemctl', 'is-enabled', unit_name],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() in ('enabled', 'enabled-runtime', 'static')
    except Exception:
        return False


def _unit_load_state(unit_name):
    """'loaded' if a unit file exists for this name, '' otherwise (or on error)."""
    try:
        result = subprocess.run(
            ['systemctl', 'show', unit_name, '-p', 'LoadState', '--value'],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ''


def _present_names(candidates, live_names):
    return [c for c in candidates if c in live_names]


def _has_pipewire_audio(live_names):
    return 'pipewire-pulse.service' in live_names or 'pipewire.service' in live_names


def evaluate_rules(services):
    """
    Cross static rule definitions against the live service list from
    services.systemd.list_services(). Returns two lists:
      actionable   — suggestions the user can select and apply (disable)
      informative  — boot/power findings, shown separately, no action here
    """
    live_names = {svc['name'] for svc in services}
    actionable = []

    # 1. Hardware absent
    is_vm, _hv = detect_virtualization()
    if not is_vm:
        for name in _present_names(VM_GUEST_SERVICES, live_names):
            actionable.append({
                'service': name, 'category': 'hardware', 'resource': 'ram',
                'reason_key': 'opt.reason.no_vm', 'reason_args': {}, 'risk': 'low',
            })

    if not has_bluetooth_adapter():
        for name in _present_names(BLUETOOTH_SERVICES, live_names):
            actionable.append({
                'service': name, 'category': 'hardware', 'resource': 'ram',
                'reason_key': 'opt.reason.no_bluetooth', 'reason_args': {}, 'risk': 'low',
            })

    if not has_wifi_adapter():
        for name in _present_names(WIFI_SERVICES, live_names):
            if _is_enabled(name):
                actionable.append({
                    'service': name, 'category': 'hardware', 'resource': 'ram',
                    'reason_key': 'opt.reason.no_wifi', 'reason_args': {}, 'risk': 'medium',
                })

    # 2. Redundant stacks
    if _has_pipewire_audio(live_names):
        for name in _present_names(AUDIO_REDUNDANT_SERVICES, live_names):
            if _is_enabled(name):
                actionable.append({
                    'service': name, 'category': 'redundant', 'resource': 'ram',
                    'reason_key': 'opt.reason.audio_redundant', 'reason_args': {}, 'risk': 'medium',
                })

    # 3. Orphans of uninstalled packages
    for orphan in find_orphan_services(services):
        actionable.append({
            'service': orphan['name'], 'category': 'orphan', 'resource': 'ram',
            'reason_key': 'opt.reason.orphan_pkg',
            'reason_args': {'pkg': orphan['owner_package']}, 'risk': 'medium',
        })

    # 3b. Dangling enablement symlinks — unit files with LoadState 'not-found'
    for name, symlink_paths in find_dangling_symlinks(services).items():
        actionable.append({
            'service': name, 'category': 'orphan', 'resource': 'cleanup',
            'reason_key': 'opt.reason.orphan_symlink',
            'reason_args': {'paths': ', '.join(symlink_paths)}, 'risk': 'low',
            'action': 'remove_symlink', 'symlink_paths': symlink_paths,
        })

    # 4. Recommended maintenance: SSD/NVMe present but periodic TRIM not enabled
    if (has_ssd_or_nvme() and _unit_load_state(FSTRIM_TIMER) == 'loaded'
            and not _is_enabled(FSTRIM_TIMER)):
        actionable.append({
            'service': FSTRIM_TIMER, 'category': 'maintenance', 'resource': 'disk',
            'reason_key': 'opt.reason.fstrim_missing', 'reason_args': {}, 'risk': 'low',
            'action': 'enable',
        })

    # 5. Boot-blocking network wait. Disabling it does not slow down or break
    # networking — NetworkManager itself still starts at the same speed and
    # connects asynchronously. It only stops the *boot sequence* from pausing
    # until the network is fully up. Marked 'medium' rather than 'low' because
    # Soplos targets novice users: on a desktop this is safe, but a machine
    # with something that genuinely needs network at boot (NFS/CIFS mounts,
    # a VPN, a startup backup job) could race against it, and a novice would
    # not know to check for that before applying.
    if (NETWORK_WAIT_ONLINE_SERVICE in live_names
            and _is_enabled(NETWORK_WAIT_ONLINE_SERVICE)):
        actionable.append({
            'service': NETWORK_WAIT_ONLINE_SERVICE, 'category': 'boot_block', 'resource': 'boot',
            'reason_key': 'opt.reason.netm_wait_online', 'reason_args': {}, 'risk': 'medium',
            'action': 'disable',
        })

    # 6. Boot time / power — informative only, not offered as an action here
    informative = []
    for entry in get_boot_blame():
        if entry['time_ms'] >= BOOT_BLAME_THRESHOLD_MS:
            informative.append({
                'service': entry['name'], 'category': 'boot', 'resource': 'boot',
                'detail': entry['time_ms'],
            })
    for timer in get_frequent_timers(FREQUENT_TIMER_THRESHOLD_S):
        informative.append({
            'service': timer['name'], 'category': 'power', 'resource': 'power',
            'detail': timer['interval_seconds'],
        })

    return actionable, informative
