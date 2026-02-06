#!/usr/bin/env python3
"""
Cross-Platform Setup Script for URL Shortener
Handles initial project setup: dependencies, environment, database, and frontend.
Works on Windows, Linux, and macOS.
"""

import sys
import os
import platform
import subprocess
import shutil
import socket
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


def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def is_windows():
    """Check if running on Windows"""
    return platform.system() == "Windows"


def check_python_version():
    """Verify Python version is 3.8 or higher"""
    print_header("Checking Python Version")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version_str} found")
        return True
    else:
        print_error(f"Python {version_str} found, but 3.8+ is required")
        return False


def check_command_exists(command, name=None):
    """Check if a command exists in PATH"""
    if name is None:
        name = command

    path = shutil.which(command)
    if path:
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True, timeout=5
            )
            version = (
                result.stdout.split("\n")[0]
                if result.stdout
                else result.stderr.split("\n")[0]
            )
            print_success(f"{name} found: {version.strip()}")
            return True
        except Exception:
            print_success(f"{name} found at {path}")
            return True
    else:
        print_error(f"{name} not found in PATH")
        return False


def check_postgresql():
    """Check if PostgreSQL is accessible"""
    print_header("Checking PostgreSQL")

    if not shutil.which("psql"):
        print_error("PostgreSQL not found in PATH")
        print_info("Please install PostgreSQL and ensure it's running")
        if is_windows():
            print_info(
                "Windows: Download from https://www.postgresql.org/download/windows/"
            )
        else:
            print_info(
                "Linux: sudo apt install postgresql  OR  sudo yum install postgresql"
            )
        return False

    print_success("PostgreSQL client found")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", 5432))
    sock.close()

    if result == 0:
        print_success("PostgreSQL is running on port 5432")
        return True
    else:
        print_error("PostgreSQL is not running on port 5432")
        print_info("Please start PostgreSQL service:")
        if is_windows():
            print_info(
                "  Windows: Open Services (services.msc) and start 'postgresql' service"
            )
        else:
            print_info("  Linux: sudo systemctl start postgresql")
        return False


def check_redis():
    """Check if Redis is accessible"""
    print_header("Checking Redis")
    has_redis = shutil.which("redis-cli") or shutil.which("redis-server")

    if not has_redis:
        print_warning("Redis not found in PATH")
        print_info("Please install Redis:")
        if is_windows():
            print_info(
                "  Windows: https://redis.io/docs/getting-started/installation/install-redis-on-windows/"
            )
        else:
            print_info("  Linux: sudo apt install redis  OR  sudo yum install redis")
    else:
        print_success("Redis client found")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", 6379))
    sock.close()

    if result == 0:
        print_success("Redis is running on port 6379")
        return True
    else:
        print_error("Redis is not running on port 6379")
        print_info("Please start Redis service:")
        if is_windows():
            print_info("  Windows: redis-server")
        else:
            print_info("  Linux: sudo systemctl start redis")
        return False


def check_node_or_bun():
    """Check for Bun or Node.js"""
    print_header("Checking Node.js/Bun")

    has_bun = check_command_exists("bun", "Bun")
    has_node = check_command_exists("node", "Node.js")
    has_npm = check_command_exists("npm", "npm")

    if has_bun:
        return "bun"
    elif has_node and has_npm:
        return "npm"
    else:
        print_error("Neither Bun nor Node.js/npm found")
        print_info("Please install one of:")
        print_info("  Bun: https://bun.sh/")
        print_info("  Node.js: https://nodejs.org/")
        return None


def setup_environment():
    """Setup .env file from .env.example"""
    print_header("Setting Up Environment")

    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_file.exists():
        print_info(".env file already exists, skipping")
        return True

    if not env_example.exists():
        print_error(".env.example not found")
        return False

    shutil.copy(env_example, env_file)
    print_success("Created .env from .env.example")
    print_warning("Please edit .env file and configure your database credentials")
    print_info(
        "Required settings: DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, SECRET_KEY"
    )

    return True


def create_virtualenv():
    """Create Python virtual environment"""
    print_header("Setting Up Python Virtual Environment")

    venv_path = Path(".venv")

    if venv_path.exists():
        print_info("Virtual environment already exists")
        return True

    print_info("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def get_venv_python():
    """Get path to Python executable in virtual environment"""
    venv_path = Path(".venv")
    if is_windows():
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def get_venv_pip():
    """Get path to pip executable in virtual environment"""
    venv_path = Path(".venv")
    if is_windows():
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"


def install_backend_dependencies():
    """Install Python dependencies from requirements.txt"""
    print_header("Installing Backend Dependencies")

    requirements = Path("requirements.txt")
    if not requirements.exists():
        print_error("requirements.txt not found")
        return False

    pip_exe = get_venv_pip()

    print_info("Installing Python packages (this may take a few minutes)...")
    try:
        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], check=True)
        print_success("Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def run_migrations():
    """Run Django database migrations"""
    print_header("Running Database Migrations")

    python_exe = get_venv_python()

    print_info("Running migrations...")
    try:
        subprocess.run([str(python_exe), "manage.py", "migrate"], check=True)
        print_success("Database migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to run migrations: {e}")
        print_info("Make sure PostgreSQL is running and .env is configured correctly")
        return False


def seed_database():
    """Seed database with test data"""
    print_header("Seeding Database")

    python_exe = get_venv_python()

    print_info("Creating test data...")
    try:
        subprocess.run(
            [
                str(python_exe),
                "manage.py",
                "seed_data",
                "--users",
                "5",
                "--urls-per-user",
                "20",
            ],
            check=True,
        )
        print_success("Database seeded with test data")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to seed database: {e}")
        return False


def install_frontend_dependencies(package_manager):
    """Install frontend dependencies"""
    print_header("Installing Frontend Dependencies")

    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print_error("frontend/ directory not found")
        return False

    package_json = frontend_path / "package.json"
    if not package_json.exists():
        print_error("frontend/package.json not found")
        return False

    print_info(f"Installing frontend packages with {package_manager}...")
    try:
        subprocess.run([package_manager, "install"], cwd=str(frontend_path), check=True)
        print_success("Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install frontend dependencies: {e}")
        return False


def print_final_instructions():
    """Print final setup instructions"""
    print_header("Setup Complete!")

    print(f"{Colors.GREEN}✓ All setup steps completed successfully!{Colors.RESET}\n")

    print(f"{Colors.BOLD}Next Steps:{Colors.RESET}")
    print(f"  1. Edit {Colors.BLUE}.env{Colors.RESET} file if you haven't already")
    print(f"  2. Start all services: {Colors.GREEN}python run.py{Colors.RESET}")
    print(f"  3. Access the application:")
    print(f"     - Frontend: {Colors.BLUE}http://localhost:3000{Colors.RESET}")
    print(f"     - Backend API: {Colors.BLUE}http://localhost:8000{Colors.RESET}")
    print(f"     - Admin Panel: {Colors.BLUE}http://localhost:3000/admin{Colors.RESET}")
    print(
        f"\n  Default login: {Colors.YELLOW}admin_tester{Colors.RESET} / {Colors.YELLOW}Password123!{Colors.RESET}"
    )
    print(
        f"\n  To stop services: {Colors.RED}python stop.py{Colors.RESET} or press Ctrl+C\n"
    )


def main():
    """Main setup process"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}URL Shortener - Setup Script{Colors.RESET}")
    print(
        f"{Colors.BLUE}Cross-platform setup for Windows, Linux, and macOS{Colors.RESET}\n"
    )

    all_passed = True

    if not check_python_version():
        return 1

    if not check_postgresql():
        all_passed = False

    if not check_redis():
        all_passed = False

    package_manager = check_node_or_bun()
    if not package_manager:
        all_passed = False

    if not all_passed:
        print_error("\nSome required services are not running or installed.")
        print_info("Please fix the issues above and run setup.py again.")
        return 1

    if not setup_environment():
        return 1

    if not create_virtualenv():
        return 1

    if not install_backend_dependencies():
        return 1

    if not run_migrations():
        print_warning("Migrations failed. You may need to:")
        print_info("  1. Edit .env with correct database credentials")
        print_info("  2. Create the database manually")
        print_info("  3. Run: python manage.py migrate")
        return 1

    if not seed_database():
        print_warning("Seeding failed, but you can continue. Run manually later:")
        print_info("  python manage.py seed_data --users 5 --urls-per-user 20")

    if not install_frontend_dependencies(package_manager):
        return 1

    print_final_instructions()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
