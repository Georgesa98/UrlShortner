#!/usr/bin/env python3
"""
Cross-Platform Run Script for URL Shortener
Starts all required services: Django, Celery Worker, Celery Beat, and Next.js Frontend
Works on Windows, Linux, and macOS.
"""

import sys
import os
import platform
import subprocess
import signal
import time
import json
import socket
import threading
from pathlib import Path
from queue import Queue


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


SERVICE_COLORS = {
    "Django": Colors.GREEN,
    "Celery Worker": Colors.YELLOW,
    "Celery Beat": Colors.MAGENTA,
    "Frontend": Colors.CYAN,
}


def is_windows():
    """Check if running on Windows"""
    return platform.system() == "Windows"


def print_service_log(service_name, message):
    """Print a colored log message for a service"""
    color = SERVICE_COLORS.get(service_name, Colors.BLUE)
    print(f"{color}[{service_name}]{Colors.RESET} {message.rstrip()}")


def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_error(message):
    print(f"{Colors.RED}✗{Colors.RESET} {message}")


def print_info(message):
    print(f"{Colors.BLUE}⚙{Colors.RESET} {message}")


def print_header(message):
    print(f"\n{Colors.BOLD}{message}{Colors.RESET}")


def check_port_available(port, service_name="Service"):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", port))
    sock.close()

    if result == 0:
        print_error(f"Port {port} is already in use (required for {service_name})")
        return False
    return True


def check_service_running(port, service_name):
    """Check if a service is accessible on a port"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", port))
    sock.close()

    if result == 0:
        print_success(f"{service_name} connection verified (port {port})")
        return True
    else:
        print_error(f"{service_name} is not accessible on port {port}")
        return False


def get_venv_python():
    """Get path to Python executable in virtual environment"""
    venv_path = Path(".venv")
    if not venv_path.exists():
        print_error("Virtual environment not found. Run 'python setup.py' first.")
        sys.exit(1)

    if is_windows():
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def get_package_manager():
    """Determine which package manager to use for frontend"""
    import shutil

    if shutil.which("bun"):
        return "bun"
    elif shutil.which("npm"):
        return "npm"
    else:
        print_error("Neither Bun nor npm found. Cannot start frontend.")
        return None


def stream_output(process, service_name, output_queue):
    """Stream process output to console with service name prefix"""
    try:
        for line in iter(process.stdout.readline, ""):
            if line:
                print_service_log(service_name, line)
                output_queue.put((service_name, line))
    except Exception as e:
        print_error(f"Error streaming {service_name} output: {e}")


def load_env_for_subprocess():
    """Load environment variables from .env file for subprocess"""
    env = os.environ.copy()
    env_file = Path('.env')
    
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
    
    # Ensure required django-configurations variables are set
    env.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    env.setdefault('DJANGO_CONFIGURATION', 'FrontendDev')
    
    return env


def start_django(processes):
    """Start Django development server"""
    print_info("Starting Django development server...")

    python_exe = get_venv_python()

    cmd = [str(python_exe), "manage.py", "runserver", "0.0.0.0:8000"]

    try:
        if is_windows():
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid,
            )

        processes["Django"] = process
        return process
    except Exception as e:
        print_error(f"Failed to start Django: {e}")
        return None


def start_celery_worker(processes):
    """Start Celery worker"""
    print_info("Starting Celery worker...")

    python_exe = get_venv_python()
    
    # Load environment variables from .env file
    env = load_env_for_subprocess()

    if is_windows():
        cmd = [
            str(python_exe),
            "-m",
            "celery",
            "-A",
            "config",
            "worker",
            "--pool=solo",
            "--loglevel=info",
        ]
    else:
        cmd = [
            str(python_exe),
            "-m",
            "celery",
            "-A",
            "config",
            "worker",
            "--loglevel=info",
        ]

    try:
        if is_windows():
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                preexec_fn=os.setsid,
            )

        processes["Celery Worker"] = process
        return process
    except Exception as e:
        print_error(f"Failed to start Celery worker: {e}")
        return None


def start_celery_beat(processes):
    """Start Celery beat scheduler"""
    print_info("Starting Celery beat scheduler...")

    python_exe = get_venv_python()
    
    # Load environment variables from .env file
    env = load_env_for_subprocess()

    cmd = [
        str(python_exe),
        "-m",
        "celery",
        "-A",
        "config",
        "beat",
        "--loglevel=info",
        "--scheduler",
        "django_celery_beat.schedulers:DatabaseScheduler",
    ]

    try:
        if is_windows():
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                preexec_fn=os.setsid,
            )

        processes["Celery Beat"] = process
        return process
    except Exception as e:
        print_error(f"Failed to start Celery beat: {e}")
        return None


def start_frontend(processes):
    """Start Next.js frontend"""
    print_info("Starting Next.js frontend...")

    package_manager = get_package_manager()
    if not package_manager:
        return None

    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print_error("frontend/ directory not found")
        return None

    cmd = [package_manager, "run", "dev"]

    try:
        if is_windows():
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(frontend_path),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(frontend_path),
                preexec_fn=os.setsid,
            )

        processes["Frontend"] = process
        return process
    except Exception as e:
        print_error(f"Failed to start frontend: {e}")
        return None


def save_pids(processes):
    """Save process PIDs to file"""
    pids = {name: proc.pid for name, proc in processes.items()}
    with open(".running_pids.json", "w") as f:
        json.dump(pids, f, indent=2)


def cleanup_processes(processes):
    """Terminate all running processes"""
    print_header("\n🛑 Shutting down services...")

    for service_name, process in processes.items():
        if process and process.poll() is None:
            print_info(f"Stopping {service_name} (PID {process.pid})...")
            try:
                if is_windows():
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                        capture_output=True,
                    )
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

                try:
                    process.wait(timeout=5)
                    print_success(f"Stopped {service_name}")
                except subprocess.TimeoutExpired:
                    if is_windows():
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                            capture_output=True,
                        )
                    else:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    print_success(f"Force stopped {service_name}")
            except Exception as e:
                print_error(f"Error stopping {service_name}: {e}")

    pid_file = Path(".running_pids.json")
    if pid_file.exists():
        pid_file.unlink()

    print_success("All services stopped")


def main():
    """Main execution"""
    print(
        f"\n{Colors.BOLD}{Colors.BLUE}🚀 Starting URL Shortener Services{Colors.RESET}\n"
    )

    print_header("Running Pre-flight Checks...")

    if not check_service_running(5432, "PostgreSQL"):
        print_error("Cannot start without PostgreSQL. Please start it first.")
        return 1

    if not check_service_running(6379, "Redis"):
        print_error("Cannot start without Redis. Please start it first.")
        return 1

    if not check_port_available(8000, "Django"):
        return 1

    if not check_port_available(3000, "Frontend"):
        return 1

    print_success("All pre-flight checks passed")

    processes = {}
    output_queue = Queue()

    print_header("\nStarting Services...")

    django_proc = start_django(processes)
    if not django_proc:
        cleanup_processes(processes)
        return 1

    celery_worker_proc = start_celery_worker(processes)
    if not celery_worker_proc:
        cleanup_processes(processes)
        return 1

    celery_beat_proc = start_celery_beat(processes)
    if not celery_beat_proc:
        cleanup_processes(processes)
        return 1

    frontend_proc = start_frontend(processes)
    if not frontend_proc:
        cleanup_processes(processes)
        return 1

    save_pids(processes)

    time.sleep(2)

    threads = []
    for service_name, process in processes.items():
        thread = threading.Thread(
            target=stream_output,
            args=(process, service_name, output_queue),
            daemon=True,
        )
        thread.start()
        threads.append(thread)

    print(f"\n{Colors.BOLD}{'━' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ All services are running!{Colors.RESET}")
    print(f"{Colors.BOLD}{'━' * 60}{Colors.RESET}")
    print(
        f"   {Colors.BOLD}Frontend:{Colors.RESET}  {Colors.CYAN}http://localhost:3000{Colors.RESET}"
    )
    print(
        f"   {Colors.BOLD}Backend:{Colors.RESET}   {Colors.CYAN}http://localhost:8000{Colors.RESET}"
    )
    print(
        f"   {Colors.BOLD}Admin:{Colors.RESET}     {Colors.CYAN}http://localhost:3000/admin{Colors.RESET}"
    )
    print(f"{Colors.BOLD}{'━' * 60}{Colors.RESET}")
    print(f"\n{Colors.YELLOW}Press Ctrl+C to stop all services...{Colors.RESET}\n")

    def signal_handler(signum, frame):
        cleanup_processes(processes)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    if not is_windows():
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            for service_name, process in list(processes.items()):
                if process.poll() is not None:
                    print_error(
                        f"{service_name} has stopped unexpectedly (exit code: {process.poll()})"
                    )
                    cleanup_processes(processes)
                    return 1

            time.sleep(1)
    except KeyboardInterrupt:
        cleanup_processes(processes)
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
