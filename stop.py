#!/usr/bin/env python3
"""
Cross-Platform Stop Script for URL Shortener
Gracefully stops all running services.
Works on Windows, Linux, and macOS.
"""

import sys
import os
import platform
import subprocess
import signal
import json
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_error(message):
    print(f"{Colors.RED}✗{Colors.RESET} {message}")


def print_info(message):
    print(f"{Colors.BLUE}⚙{Colors.RESET} {message}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")


def is_windows():
    """Check if running on Windows"""
    return platform.system() == "Windows"


def is_process_running(pid):
    """Check if a process with given PID is running"""
    try:
        if is_windows():
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.SubprocessError):
        return False


def terminate_process(pid, service_name, force=False):
    """Terminate a process by PID"""
    if not is_process_running(pid):
        print_warning(f"{service_name} (PID {pid}) is not running")
        return True

    try:
        if is_windows():
            if force:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    capture_output=True,
                    check=True,
                )
                print_success(f"Force stopped {service_name} (PID {pid})")
            else:
                subprocess.run(
                    ["taskkill", "/T", "/PID", str(pid)],
                    capture_output=True,
                    check=True,
                )
                print_success(f"Stopped {service_name} (PID {pid})")
        else:
            try:
                if force:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                    print_success(f"Force stopped {service_name} (PID {pid})")
                else:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    print_success(f"Stopped {service_name} (PID {pid})")
            except ProcessLookupError:
                if force:
                    os.kill(pid, signal.SIGKILL)
                else:
                    os.kill(pid, signal.SIGTERM)
                print_success(f"Stopped {service_name} (PID {pid})")

        return True
    except subprocess.CalledProcessError:
        print_error(f"Failed to stop {service_name} (PID {pid})")
        return False
    except OSError as e:
        if e.errno == 3:
            print_warning(f"{service_name} (PID {pid}) already stopped")
            return True
        else:
            print_error(f"Error stopping {service_name} (PID {pid}): {e}")
            return False


def stop_all_services():
    """Stop all services listed in .running_pids.json"""
    pid_file = Path(".running_pids.json")

    if not pid_file.exists():
        print_warning("No running services found (.running_pids.json not found)")
        print_info("Services may have been stopped already or never started")
        return 0

    try:
        with open(pid_file, "r") as f:
            pids = json.load(f)
    except json.JSONDecodeError:
        print_error("Failed to read .running_pids.json (corrupted file)")
        return 1
    except Exception as e:
        print_error(f"Error reading PID file: {e}")
        return 1

    if not pids:
        print_warning("No PIDs found in .running_pids.json")
        pid_file.unlink()
        return 0

    print(
        f"\n{Colors.BOLD}{Colors.BLUE}🛑 Stopping URL Shortener Services{Colors.RESET}\n"
    )

    stopped_count = 0
    failed_count = 0

    print_info("Attempting graceful shutdown...")
    for service_name, pid in pids.items():
        if terminate_process(pid, service_name, force=False):
            stopped_count += 1
        else:
            failed_count += 1

    if failed_count > 0:
        print_info("Waiting for processes to terminate...")
        time.sleep(3)

        print_info("Force stopping remaining processes...")
        for service_name, pid in pids.items():
            if is_process_running(pid):
                if terminate_process(pid, service_name, force=True):
                    stopped_count += 1
                    failed_count -= 1

    try:
        pid_file.unlink()
        print_success("Cleaned up PID file")
    except Exception as e:
        print_warning(f"Could not remove PID file: {e}")

    print(f"\n{Colors.BOLD}{'━' * 60}{Colors.RESET}")
    if failed_count == 0:
        print(
            f"{Colors.BOLD}{Colors.GREEN}✅ All services stopped successfully{Colors.RESET}"
        )
    else:
        print(
            f"{Colors.BOLD}{Colors.YELLOW}⚠ Stopped {stopped_count} service(s), {failed_count} failed{Colors.RESET}"
        )
    print(f"{Colors.BOLD}{'━' * 60}{Colors.RESET}\n")

    return 0 if failed_count == 0 else 1


def kill_by_port(port, service_name):
    """Kill process using a specific port (fallback method)"""
    print_info(f"Looking for {service_name} on port {port}...")

    try:
        if is_windows():
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if parts:
                        pid = int(parts[-1])
                        terminate_process(pid, service_name, force=True)
                        return True
        else:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True
            )
            if result.stdout:
                pid = int(result.stdout.strip())
                terminate_process(pid, service_name, force=True)
                return True
    except Exception as e:
        print_error(f"Error finding process on port {port}: {e}")

    return False


def emergency_stop():
    """Emergency stop: Kill processes by known ports"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠ Emergency Stop Mode{Colors.RESET}")
    print_info("Looking for services by port numbers...\n")

    killed_any = False

    ports = {
        8000: "Django",
        3000: "Frontend",
    }

    for port, service_name in ports.items():
        if kill_by_port(port, service_name):
            killed_any = True

    if killed_any:
        print_success("Found and stopped services")

        pid_file = Path(".running_pids.json")
        if pid_file.exists():
            pid_file.unlink()

        return 0
    else:
        print_warning("No services found on known ports")
        return 1


def main():
    """Main execution"""
    result = stop_all_services()

    if result != 0:
        print_info("\nTip: Run with --force flag to search by port numbers")
        if "--force" in sys.argv or "-f" in sys.argv:
            return emergency_stop()

    return result


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stop cancelled by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
