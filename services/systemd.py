import subprocess

def list_services():
    """
    Returns a list of all systemd services with their status.
    Each item is a dict: {name, description, loaded, active, sub, status}
    """
    services = []
    try:
        output = subprocess.check_output(
            ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--no-legend"],
            universal_newlines=True
        )
        for line in output.strip().split('\n'):
            if not line:
                continue
            parts = line.split(None, 4)
            if len(parts) < 5:
                continue
            name, load, active, sub, description = parts
            services.append({
                "name": name,
                "loaded": load,
                "active": active,
                "sub": sub,
                "description": description
            })
    except Exception as e:
        print(f"Error listing services: {e}")
    return services

def get_service_status(service_name):
    """
    Returns the status of a specific service.
    """
    try:
        output = subprocess.check_output(
            ["systemctl", "status", service_name, "--no-pager"],
            universal_newlines=True
        )
        return output
    except subprocess.CalledProcessError as e:
        return e.output

def start_service(service_name):
    return subprocess.call(["systemctl", "start", service_name]) == 0

def stop_service(service_name):
    return subprocess.call(["systemctl", "stop", service_name]) == 0

def restart_service(service_name):
    return subprocess.call(["systemctl", "restart", service_name]) == 0

def enable_service(service_name):
    return subprocess.call(["systemctl", "enable", service_name]) == 0

def disable_service(service_name):
    return subprocess.call(["systemctl", "disable", service_name]) == 0
