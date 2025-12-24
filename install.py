#!/usr/bin/env python3
"""
RNS Over Meshtastic Interactive Installer
Automated setup for Reticulum Network Stack over Meshtastic devices
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def prompt_yes_no(question, default=True):
    """Prompt user for yes/no answer"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{Colors.CYAN}? {question} [{default_str}]: {Colors.END}").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print_error("Please answer 'y' or 'n'")

def prompt_choice(question, choices, default=0):
    """Prompt user to choose from a list"""
    print(f"\n{Colors.CYAN}? {question}{Colors.END}")
    for i, choice in enumerate(choices, 1):
        marker = "→" if i-1 == default else " "
        print(f"  {marker} {i}. {choice}")

    while True:
        response = input(f"{Colors.CYAN}Enter choice [1-{len(choices)}] (default: {default+1}): {Colors.END}").strip()
        if not response:
            return default
        try:
            choice = int(response) - 1
            if 0 <= choice < len(choices):
                return choice
            print_error(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print_error("Please enter a valid number")

def check_python_version():
    """Check if Python version is adequate"""
    print_info("Checking Python version...")
    if sys.version_info < (3, 7):
        print_error(f"Python 3.7+ required, but you have {sys.version}")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_command_exists(command):
    """Check if a command exists"""
    return shutil.which(command) is not None

def run_command(command, description, check=True):
    """Run a shell command with error handling"""
    print_info(f"{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success(f"{description} completed")
            return True, result.stdout
        else:
            print_error(f"{description} failed: {result.stderr}")
            return False, result.stderr
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed: {e}")
        return False, str(e)

def install_pip_package(package, description=None):
    """Install a Python package via pip"""
    desc = description or f"Installing {package}"
    cmd = f"{sys.executable} -m pip install {package}"
    return run_command(cmd, desc)

def detect_serial_ports():
    """Detect available serial ports"""
    print_info("Scanning for serial devices...")
    ports = []

    if platform.system() == "Linux":
        # Check common Linux serial ports
        for pattern in ["/dev/ttyUSB*", "/dev/ttyACM*"]:
            result = subprocess.run(f"ls {pattern} 2>/dev/null", shell=True, capture_output=True, text=True)
            if result.stdout:
                ports.extend(result.stdout.strip().split('\n'))

    elif platform.system() == "Darwin":
        # macOS
        result = subprocess.run("ls /dev/cu.* 2>/dev/null", shell=True, capture_output=True, text=True)
        if result.stdout:
            ports.extend(result.stdout.strip().split('\n'))

    elif platform.system() == "Windows":
        # Windows - try to import serial.tools.list_ports
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
        except ImportError:
            print_warning("pyserial not installed yet, cannot detect COM ports")

    return [p for p in ports if p]  # Filter empty strings

def create_rns_config(interface_type, port=None, ble_port=None, tcp_port=None, data_speed=8):
    """Create Reticulum configuration file"""
    print_info("Creating Reticulum configuration...")

    config_dir = Path.home() / ".reticulum"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config"

    # Base configuration
    config = """[reticulum]
enable_transport = yes
share_instance = yes
shared_instance_port = 37428
instance_control_port = 37429

[logging]
loglevel = 4

[interfaces]
  [[Meshtastic Interface]]
    type = Meshtastic_Interface
    enabled = yes
"""

    # Add interface-specific configuration
    if interface_type == "serial" and port:
        config += f"    port = {port}\n"
    elif interface_type == "ble" and ble_port:
        config += f"    ble_port = {ble_port}\n"
    elif interface_type == "tcp" and tcp_port:
        config += f"    tcp_port = {tcp_port}\n"

    config += f"    data_speed = {data_speed}\n"

    # Write config file
    try:
        with open(config_file, 'w') as f:
            f.write(config)
        print_success(f"Configuration saved to {config_file}")
        return True
    except Exception as e:
        print_error(f"Failed to create config: {e}")
        return False

def copy_interface_file():
    """Copy Meshtastic_Interface.py to RNS interfaces directory"""
    print_info("Installing Meshtastic interface for RNS...")

    rns_interfaces_dir = Path.home() / ".reticulum" / "interfaces"
    rns_interfaces_dir.mkdir(parents=True, exist_ok=True)

    # Source file in current directory
    source = Path("Interface/Meshtastic_Interface.py")
    if not source.exists():
        print_error(f"Interface file not found: {source}")
        return False

    # Destination
    dest = rns_interfaces_dir / "Meshtastic_Interface.py"

    try:
        shutil.copy2(source, dest)
        print_success(f"Interface installed to {dest}")
        return True
    except Exception as e:
        print_error(f"Failed to copy interface: {e}")
        return False

def configure_linux_permissions():
    """Add user to dialout group on Linux"""
    if platform.system() != "Linux":
        return True

    print_info("Configuring serial port permissions...")
    username = os.getenv("USER")

    success, _ = run_command(
        f"sudo usermod -a -G dialout {username}",
        "Adding user to dialout group",
        check=False
    )

    if success:
        print_warning("You need to log out and log back in for permission changes to take effect")
    return success

def main():
    """Main installer function"""
    print_header("RNS Over Meshtastic Installer")

    print(f"{Colors.BOLD}This installer will help you set up:{Colors.END}")
    print("  • Reticulum Network Stack (RNS)")
    print("  • Meshtastic Python library")
    print("  • RNS Meshtastic interface")
    print("  • Optional: RNS applications (NomadNet, Meshchat)\n")

    if not prompt_yes_no("Continue with installation?", True):
        print_info("Installation cancelled")
        return

    # Check Python version
    print_header("Step 1: Checking Prerequisites")
    if not check_python_version():
        sys.exit(1)

    # Check pip
    if not check_command_exists("pip") and not check_command_exists("pip3"):
        print_error("pip is not installed. Please install pip first.")
        sys.exit(1)
    print_success("pip is installed")

    # Install core packages
    print_header("Step 2: Installing Core Packages")

    if prompt_yes_no("Install required Python packages?", True):
        packages = [
            ("rns", "Reticulum Network Stack"),
            ("meshtastic", "Meshtastic Python library"),
            ("pyserial", "Serial port library"),
            ("pypubsub", "Publish-subscribe library")
        ]

        for package, description in packages:
            success, _ = install_pip_package(package, f"Installing {description}")
            if not success:
                print_error(f"Failed to install {package}")
                if not prompt_yes_no("Continue anyway?", False):
                    sys.exit(1)

    # Copy interface file
    print_header("Step 3: Installing Meshtastic Interface")
    if not copy_interface_file():
        print_error("Failed to install interface file")
        sys.exit(1)

    # Configure Meshtastic connection
    print_header("Step 4: Configuring Meshtastic Connection")

    connection_types = ["Serial (USB)", "Bluetooth LE", "TCP/IP", "Skip configuration"]
    connection_choice = prompt_choice("How will you connect to your Meshtastic device?", connection_types, 0)

    port = None
    ble_port = None
    tcp_port = None

    if connection_choice == 0:  # Serial
        ports = detect_serial_ports()
        if ports:
            print_success(f"Found {len(ports)} serial device(s)")
            port_choice = prompt_choice("Select serial port:", ports + ["Enter manually"], 0)
            if port_choice < len(ports):
                port = ports[port_choice]
            else:
                port = input(f"{Colors.CYAN}Enter serial port path: {Colors.END}").strip()
        else:
            print_warning("No serial devices detected")
            port = input(f"{Colors.CYAN}Enter serial port path (e.g., /dev/ttyUSB0): {Colors.END}").strip()

        # Configure Linux permissions if needed
        if platform.system() == "Linux":
            configure_linux_permissions()

    elif connection_choice == 1:  # BLE
        ble_port = input(f"{Colors.CYAN}Enter Meshtastic BLE device ID (e.g., short_1234): {Colors.END}").strip()

    elif connection_choice == 2:  # TCP
        tcp_port = input(f"{Colors.CYAN}Enter TCP address:port (e.g., 127.0.0.1:4403): {Colors.END}").strip()

    # Configure LoRa speed
    if connection_choice != 3:
        print(f"\n{Colors.BOLD}LoRa Speed Settings:{Colors.END}")
        print("  8 - SHORT_TURBO (0.4s) - Recommended for RNS")
        print("  6 - SHORT_FAST (1s)")
        print("  5 - SHORT_SLOW (3s)")
        print("  4 - MEDIUM_FAST (4s)")
        print("  0 - LONG_FAST (8s) - Default")

        speed_input = input(f"{Colors.CYAN}Enter speed setting [0-8] (default: 8): {Colors.END}").strip()
        data_speed = int(speed_input) if speed_input.isdigit() else 8

        # Create RNS configuration
        interface_type = ["serial", "ble", "tcp"][connection_choice]
        create_rns_config(interface_type, port, ble_port, tcp_port, data_speed)

    # Install optional applications
    print_header("Step 5: Optional Applications")

    if prompt_yes_no("Install NomadNet (Terminal-based mesh communication)?", False):
        install_pip_package("nomadnet", "Installing NomadNet")

    if prompt_yes_no("Install rnsh (Remote shell over RNS)?", False):
        install_pip_package("rnsh", "Installing rnsh")

    if prompt_yes_no("Install Sideband (for Linux)?", False):
        install_pip_package("sbapp", "Installing Sideband")

    # Installation complete
    print_header("Installation Complete!")

    print(f"\n{Colors.BOLD}{Colors.GREEN}Next Steps:{Colors.END}")
    print(f"\n1. {Colors.BOLD}Test your setup:{Colors.END}")
    print(f"   {Colors.CYAN}rnsd{Colors.END}  # Start RNS daemon")
    print(f"   {Colors.CYAN}rnstatus{Colors.END}  # Check interface status")

    print(f"\n2. {Colors.BOLD}Configure your Meshtastic device:{Colors.END}")
    if port:
        print(f"   {Colors.CYAN}meshtastic --info{Colors.END}")
        print(f"   {Colors.CYAN}meshtastic --set lora.region US{Colors.END}")
        print(f"   {Colors.CYAN}meshtastic --set lora.modem_preset SHORT_FAST{Colors.END}")

    print(f"\n3. {Colors.BOLD}Try RNS applications:{Colors.END}")
    print(f"   {Colors.CYAN}nomadnet{Colors.END}  # Launch NomadNet")
    print(f"   {Colors.CYAN}rncp file.txt <hash>:remote.txt{Colors.END}  # Transfer files")

    print(f"\n{Colors.BOLD}Documentation:{Colors.END}")
    print(f"   • Setup Guide: RNS_Meshtastic_Setup_Guide.md")
    print(f"   • README: README.md")
    print(f"   • RNS Manual: https://reticulum.network/manual/")

    if platform.system() == "Linux" and connection_choice == 0:
        print(f"\n{Colors.YELLOW}⚠ Remember to log out and log back in for serial port permissions!{Colors.END}")

    print(f"\n{Colors.GREEN}Happy meshing!{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Installation cancelled by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
