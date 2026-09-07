import os
import subprocess


def detect_virtualization():
    """Return (is_vm, hypervisor_key) using systemd-detect-virt with a DMI fallback."""
    try:
        result = subprocess.run(
            ['systemd-detect-virt'], capture_output=True, text=True, timeout=5
        )
        virt = result.stdout.strip().lower()
        if virt and virt != 'none':
            return True, virt
    except Exception:
        pass

    for dmi_file in ('/sys/class/dmi/id/sys_vendor', '/sys/class/dmi/id/product_name'):
        try:
            with open(dmi_file, 'r') as f:
                content = f.read().lower()
            if 'vmware' in content:
                return True, 'vmware'
            if 'virtualbox' in content:
                return True, 'oracle'
            if 'qemu' in content or 'kvm' in content:
                return True, 'kvm'
            if 'microsoft' in content:
                return True, 'microsoft'
        except Exception:
            continue

    return False, None


def has_bluetooth_adapter():
    """True if a Bluetooth controller is registered by the kernel."""
    bt_class_dir = '/sys/class/bluetooth'
    try:
        return os.path.isdir(bt_class_dir) and len(os.listdir(bt_class_dir)) > 0
    except Exception:
        return False


def has_wifi_adapter():
    """True if a Wi-Fi interface (802.11 phy) is registered by the kernel."""
    ieee80211_dir = '/sys/class/ieee80211'
    try:
        return os.path.isdir(ieee80211_dir) and len(os.listdir(ieee80211_dir)) > 0
    except Exception:
        return False


def has_ssd_or_nvme():
    """True if any non-removable, non-virtual block device reports as non-rotational."""
    base = '/sys/block'
    try:
        for dev in os.listdir(base):
            if dev.startswith(('loop', 'sr', 'ram', 'zram')):
                continue
            rota_path = os.path.join(base, dev, 'queue', 'rotational')
            try:
                with open(rota_path, 'r') as f:
                    if f.read().strip() == '0':
                        return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def has_audio_hardware():
    """True if at least one sound card is registered by the kernel."""
    try:
        with open('/proc/asound/cards', 'r') as f:
            content = f.read().strip()
        return bool(content) and 'no soundcards' not in content.lower()
    except Exception:
        return True  # Unknown — assume present, never suggest removing audio blind.
