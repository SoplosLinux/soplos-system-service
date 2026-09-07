import os
import subprocess

_CHUNK_SIZE = 200

# systemd enablement symlinks live in *.wants/ and *.requires/ subdirectories
# under these unit search paths, in ascending precedence order.
_UNIT_SEARCH_DIRS = (
    '/lib/systemd/system',
    '/usr/lib/systemd/system',
    '/run/systemd/system',
    '/etc/systemd/system',
)


def _get_fragment_paths_batch(service_names):
    """
    Resolve FragmentPath for many units in as few `systemctl show` calls as
    possible (chunked to keep the command line short), instead of one
    subprocess invocation per unit — with hundreds of services on a real
    system, per-unit calls were the main reason a scan took a long time.
    """
    paths = {}
    names = list(service_names)
    for i in range(0, len(names), _CHUNK_SIZE):
        chunk = names[i:i + _CHUNK_SIZE]
        try:
            result = subprocess.run(
                ['systemctl', 'show', *chunk, '-p', 'Id', '-p', 'FragmentPath'],
                capture_output=True, text=True, timeout=30
            )
        except Exception:
            continue
        for block in result.stdout.split('\n\n'):
            unit_id = None
            fragment_path = None
            for line in block.splitlines():
                if line.startswith('Id='):
                    unit_id = line[len('Id='):]
                elif line.startswith('FragmentPath='):
                    fragment_path = line[len('FragmentPath='):]
            if unit_id:
                paths[unit_id] = fragment_path or None
    return paths


def _get_owners_batch(fragment_paths):
    """
    Resolve the owning dpkg package for many unit files in as few `dpkg -S`
    calls as possible, instead of one call per file.
    """
    owners = {}
    unique_paths = sorted({p for p in fragment_paths if p})
    for i in range(0, len(unique_paths), _CHUNK_SIZE):
        chunk = unique_paths[i:i + _CHUNK_SIZE]
        try:
            result = subprocess.run(
                ['dpkg', '-S', *chunk],
                capture_output=True, text=True, timeout=30
            )
        except Exception:
            continue
        for line in result.stdout.splitlines():
            if ':' not in line:
                continue
            pkg_part, path_part = line.split(':', 1)
            path_part = path_part.strip()
            # dpkg -S prints "pkg1, pkg2: /path" when several packages share
            # ownership (e.g. via diversions) — the first one is enough here.
            owner = pkg_part.split(',')[0].strip()
            owners[path_part] = owner
    return owners


def is_package_installed(package_name):
    try:
        result = subprocess.run(
            ['dpkg', '-s', package_name],
            capture_output=True, text=True, timeout=10
        )
        return 'Status: install ok installed' in result.stdout
    except Exception:
        return False


def find_dangling_symlinks(services):
    """
    Find enablement symlinks (in *.wants/ or *.requires/ directories) that
    point at a unit whose 'not-found' LoadState means systemd cannot locate
    any unit file for it at all.

    This is the single clearest and safest kind of residual leftover there
    is: the package that shipped the unit file was removed (its postrm did
    not clean the symlink it created, common with clamav/cloud-init/connman/
    auditd-style packages) or was purged incompletely, but the enablement
    link — pure dead weight, no working directory to point to — is still
    there. Nothing is running because of it; removing it only removes the
    stale reference.
    """
    not_found_names = {
        s['name'] for s in services if s.get('loaded', '').lower() == 'not-found'
    }
    if not not_found_names:
        return {}

    dangling = {}
    for base_dir in _UNIT_SEARCH_DIRS:
        if not os.path.isdir(base_dir):
            continue
        try:
            subdirs = os.listdir(base_dir)
        except Exception:
            continue
        for sub in subdirs:
            if not (sub.endswith('.wants') or sub.endswith('.requires')):
                continue
            sub_path = os.path.join(base_dir, sub)
            try:
                entries = os.listdir(sub_path)
            except Exception:
                continue
            for entry in entries:
                if entry not in not_found_names:
                    continue
                entry_path = os.path.join(sub_path, entry)
                if os.path.islink(entry_path) and not os.path.exists(entry_path):
                    dangling.setdefault(entry, []).append(entry_path)
    return dangling


def remove_dangling_symlinks(symlink_paths):
    for path in symlink_paths:
        try:
            os.unlink(path)
        except Exception as e:
            print(f"Error removing dangling symlink {path}: {e}")


def find_orphan_services(services):
    """
    Given the list of service dicts from services.systemd.list_services(),
    return the subset that are residual: the unit is loaded (not 'not-found')
    but the dpkg package that owns the unit file is no longer installed.

    Units with no dpkg owner at all (never packaged — hand-installed or
    admin-authored) are not flagged here: there is nothing to check them
    against, and treating "unowned" as "orphan" would flag every custom
    unit an admin ever wrote.

    'not-found' units are handled separately by find_dangling_symlinks(),
    since there is no FragmentPath to check dpkg ownership against.
    """
    candidates = [s for s in services if s.get('loaded', '').lower() != 'not-found']
    names = [s['name'] for s in candidates]

    fragment_paths = _get_fragment_paths_batch(names)
    owners = _get_owners_batch(fragment_paths.values())

    orphans = []
    installed_cache = {}
    for svc in candidates:
        name = svc['name']
        fragment_path = fragment_paths.get(name)
        owner = owners.get(fragment_path) if fragment_path else None
        if not owner:
            continue
        if owner not in installed_cache:
            installed_cache[owner] = is_package_installed(owner)
        if not installed_cache[owner]:
            orphans.append({
                'name': name,
                'owner_package': owner,
                'fragment_path': fragment_path,
            })
    return orphans
