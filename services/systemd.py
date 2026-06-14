import subprocess


def list_services():
    """Return a list of all systemd service units with their status fields."""
    services = []
    try:
        result = subprocess.run(
            ['systemctl', 'list-units', '--type=service', '--all',
             '--no-pager', '--no-legend'],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split(None, 5)
            # systemctl prefixes failed/masked units with a ● bullet character
            if parts and parts[0] in ('●', '●'):
                parts = parts[1:]
            if len(parts) < 5:
                continue
            name = parts[0]
            loaded = parts[1]
            active = parts[2]
            sub = parts[3]
            description = parts[4] if len(parts) > 4 else ''
            services.append({
                'name': name,
                'loaded': loaded,
                'active': active,
                'sub': sub,
                'description': description,
            })
    except Exception as e:
        print(f"Error listing services: {e}")
    return services


def get_service_status(service_name):
    """Return the full status output of a service."""
    try:
        result = subprocess.run(
            ['systemctl', 'status', service_name, '--no-pager'],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)


def get_service_logs(service_name, lines=200):
    """Return the last N lines of journalctl output for a service."""
    try:
        result = subprocess.run(
            ['journalctl', '-u', service_name, '--no-pager',
             '-n', str(lines), '--output=short-precise'],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)


def start_service(service_name):
    result = subprocess.run(
        ['systemctl', 'start', service_name],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0, result.stderr


def stop_service(service_name):
    result = subprocess.run(
        ['systemctl', 'stop', service_name],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0, result.stderr


def restart_service(service_name):
    result = subprocess.run(
        ['systemctl', 'restart', service_name],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0, result.stderr


def enable_service(service_name):
    result = subprocess.run(
        ['systemctl', 'enable', service_name],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0, result.stderr


def disable_service(service_name):
    result = subprocess.run(
        ['systemctl', 'disable', service_name],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0, result.stderr
