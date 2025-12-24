# RNS Over Meshtastic Setup Guide

## Overview

### What is Reticulum Network Stack (RNS)?
Reticulum is a cryptography-based networking stack designed for resilient, decentralized communication over diverse mediums. It provides:
- **End-to-end encryption** by default for all communications
- **Self-configuring mesh routing** with automatic path discovery
- **Medium agnostic** design supporting LoRa, WiFi, serial, TCP/UDP, and more
- **Minimal infrastructure** requirements - works without internet or cellular networks
- **Built-in utilities** for file transfer, messaging, and remote shell access

### Why RNS over Meshtastic?
This integration combines the strengths of both technologies:
- **Meshtastic:** Provides reliable LoRa mesh networking and hardware ecosystem
- **Reticulum:** Adds encrypted applications, advanced routing, and cross-medium capabilities

**Key Benefits:**
- Use RNS applications (file transfer, messaging, LXMF) over Meshtastic hardware
- Expected throughput: ~500 bytes/second
- Works alongside existing Meshtastic nodes (propagated through the mesh)
- Ideal for data-intensive applications where Meshtastic's native capabilities are insufficient

### What This Guide Covers
This guide provides comprehensive instructions for:
1. Selecting and configuring Meshtastic hardware (ESP32, nRF52, Pico, Linux native)
2. Installing and configuring the Reticulum Network Stack
3. Setting up the RNS_Over_Meshtastic interface
4. Testing and optimizing your deployment
5. Troubleshooting common issues

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Hardware Requirements](#hardware-requirements)
3. [Software Installation](#software-installation)
4. [Configuration](#configuration)
5. [Testing the Setup](#testing-the-setup)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Features](#advanced-features)
8. [Security Considerations](#security-considerations)
9. [Performance Optimization](#performance-optimization)
10. [References](#references)

## Prerequisites

### Knowledge Requirements
- Basic understanding of networking concepts
- Familiarity with command-line interfaces
- Understanding of LoRa and mesh networking principles (helpful but not required)

### System Requirements
- Python 3.7 or higher
- Linux, macOS, or Windows operating system
- USB port for connecting Meshtastic device
- Internet connection for initial setup and software installation

## Hardware Requirements

### Hardware Selection Guide

**Radio Chip Preference:**
- **Recommended:** Devices with Semtech SX126x or LR11xx series chips (newer, better performance)
- **Older:** SX127x series (still supported but less efficient)

**Power Considerations:**
- **nRF52-based devices:** Lower power consumption, ideal for solar and battery-powered deployments
- **ESP32-based devices:** Higher power consumption but lower cost, WiFi support, and more RAM

**Popular Community Favorites (2024):**
- RAK Meshtastic Start Kit (RAK19007 + RAK4631) - nRF52, modular
- Seeed Card Tracker T1000-E - Compact, GPS tracking
- Heltec Mesh Node T114 - Low power, good value
- LILYGO LoRa T3-S3 - ESP32-S3, WiFi, flexible

**All devices can mesh together regardless of hardware differences.**

### Supported Meshtastic Devices

#### Option 1: Microcontroller-Based Devices (Portable/Mobile)

**ESP32-Based Devices:**
- **LILYGO®:** T-Beam, T-Echo, LoRa T3-S3, T-Deck
- **HELTEC®:** LoRa 32 V3, Vision Master, Mesh Node T114, Wireless Tracker
- **RAK®:** WisBlock (modular), WisMesh Pocket/Tap
- **B&Q Consulting:** Nano G1, G2, Station G1/G2
- **Elecrow:** ThinkNode, CrowPanel Advance
- **Seeed Studio:** Wio Series development boards

**nRF52-Based Devices (Lower Power):**
- **RAK®:** RAK4631 + RAK19007 Base (WisBlock Starter Kit)
- **Seeed Studio:** Card Tracker T1000-E
- Various nRF52840-based boards

**Additional Hardware:**
- USB cable (appropriate for your device)
- Optional: External antenna for improved range (SMA/U.FL)
- Optional: Battery pack (18650 for T-Beam, LiPo for others)
- Optional: GPS module (if not built-in)

#### Option 2: Raspberry Pi Pico (Budget-Friendly Option)
**Recommended for:** Low-cost nodes, experimental setups, simple deployments

**Hardware Requirements:**
- **Raspberry Pi Pico** or **Pico W** (RP2040 microcontroller, 133MHz dual-core)
- **Waveshare LoRa Module** with SX1262 transceiver (required - Pico has no built-in LoRa)
- **Frequency bands:** 410-525 MHz, 863-870 MHz, 902-930 MHz
- **Antenna:** U.FL/IPEX connector for LoRa
- **Power:** USB or 1.25mm JST battery connector

**Features:**
- **Pico W:** WiFi support (no web server/HTTP API currently)
- **Bluetooth:** Not currently supported
- **Firmware:** Flash via .uf2 file (simple drag-and-drop)

**Important Notes:**
- LoRa transmissions may interfere with USB connection
- Keep antenna away from USB port
- No web interface available
- Limited compared to ESP32 devices

#### Option 3: Linux Native Hardware (Gateway/Relay Nodes)
**Recommended for:** Always-on gateway nodes, transport/relay stations, high-traffic RNS nodes

**Supported Linux Devices:**
- **Raspberry Pi** (Zero 2, 3, 4, 400, 5) on Raspbian Bookworm
- **Luckfox Pico**
- **Generic Linux** (Debian 12, Ubuntu 22.04/24.04, Fedora 41) with USB CH341-based radios

**Compatible LoRa Hardware:**
- **SPI-based LoRa Hats** (Required - UART hats NOT supported):
  - MeshAdv-Pi v1.1
  - Adafruit RFM9x (RFM95/96/97/98)
  - Elecrow LoRa RFM95 IOT
  - Other SPI-based LoRa modules (SX126x, SX127x)
- **USB LoRa Adapters**: CH341-based USB devices (e.g., MeshStick)

**Important Notes:**
- SX1302/SX1303 chip-based hats are NOT supported
- Waveshare SX1262 and Pine64 Pinedio have known limitations with longer messages
- Bluetooth is not supported on Linux native
- Built-in web server available (port 443)
- Requires root/sudo access for GPIO and SPI
- Configuration stored in `/root/.portduino/default/prefs/`

**Advantages of Linux Native for RNS:**
- Always-on gateway capability
- Better processing power for high traffic
- Multiple interface support (I²C displays, SPI displays, keyboard)
- Systemd service for automatic startup
- Web interface for monitoring
- Ideal for transport nodes and network infrastructure

## Software Installation

### Step 1: Install Python and pip
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# On macOS (using Homebrew)
brew install python3

# On Windows
# Download and install from python.org
```

### Step 2: Install Reticulum
```bash
pip3 install rns
```

### Step 3: Install Meshtastic Python Library

#### Option A: Install via pip (Recommended for most users)
```bash
pip3 install meshtastic
```

#### Option B: Install via Native Package (Debian/Ubuntu)

**For Debian 13 (trixie) or 12 (bookworm):**
```bash
# Replace [VERSION] with 13 or 12
echo 'deb http://download.opensuse.org/repositories/network:/Meshtastic:/beta/Debian_[VERSION]/ /' | sudo tee /etc/apt/sources.list.d/network:Meshtastic:beta.list
curl -fsSL https://download.opensuse.org/repositories/network:Meshtastic:beta/Debian_[VERSION]/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/network_Meshtastic_beta.gpg > /dev/null
sudo apt update
sudo apt install meshtasticd
```

**For Ubuntu 25.04 (plucky), 24.04 LTS (noble), or 22.04 LTS (jammy):**
```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:meshtastic/beta
sudo apt install meshtasticd
```

**Note:** The native package installs `meshtasticd` (Meshtastic daemon) which includes support for USB radio connectivity, SPI radio, MUI interface, and web client. For RNS integration, you still need the Python library (Option A).

#### Option C: Install All Dependencies from requirements.txt
```bash
# Clone or download this repository, then:
pip3 install -r requirements.txt
```

### Step 4: Install PySerial
```bash
pip3 install pyserial
```

### Step 5: Flash Meshtastic Firmware

#### For ESP32-based Devices:
If your device doesn't have Meshtastic firmware:
```bash
pip3 install meshtastic-flasher
meshtastic-flasher
```
Follow the on-screen instructions to flash your device.

#### For Raspberry Pi Pico:
1. Download the appropriate firmware:
   - **Pico:** `firmware-pico-X.X.X.xxxxxxx.uf2`
   - **Pico W:** `firmware-pico-w-X.X.X.xxxxxxx.uf2`

2. Flash the firmware:
   ```bash
   # Hold BOOTSEL button while connecting Pico to USB
   # Pico will mount as a USB drive
   # Drag and drop the .uf2 file to the drive
   # Pico will automatically reboot with Meshtastic firmware
   ```

3. Download from: https://meshtastic.org/downloads

### Step 6: Linux Native Hardware Setup (Optional)

If using a Raspberry Pi or other Linux device as a Meshtastic gateway:

#### Enable SPI Interface (Raspberry Pi)
```bash
# Option 1: Using raspi-config
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable

# Option 2: Manual configuration
# Add to /boot/firmware/config.txt:
# dtparam=spi=on
# dtoverlay=spi0-0cs
```

#### Install Meshtasticd Service
The native package (installed in Step 3, Option B) includes the meshtasticd service:

```bash
# Enable and start the service
sudo systemctl enable meshtasticd
sudo systemctl start meshtasticd

# Check status
sudo systemctl status meshtasticd

# View logs
sudo journalctl -u meshtasticd -f
```

#### Configure Hardware Interface
Edit the configuration file to match your hardware:

**Primary config location:** `/etc/meshtasticd/config.yaml`
**User data location:** `/root/.portduino/default/prefs/`
**Hardware presets:** `/etc/meshtasticd/available.d/`

```yaml
# Example for Raspberry Pi with RFM95 hat
Lora:
  Module: sx127x
  CS: 7
  IRQ: 22
  Busy: -1
  Reset: 4
  DIO2: -1
  DIO3: -1
  TXen: -1
  RXen: -1
```

**Check available hardware presets:**
```bash
ls /etc/meshtasticd/available.d/
```

#### Access Web Interface
After starting meshtasticd:
```bash
# Access via browser
https://localhost
# or from another device
https://<raspberry-pi-ip>
```

#### Configure via CLI
```bash
# Connect to local meshtasticd instance
meshtastic --host localhost --info

# Set configuration (same as regular Meshtastic)
meshtastic --host localhost --set lora.region US
meshtastic --host localhost --set lora.modem_preset SHORT_FAST
```

#### Best Practices for Linux Native Deployment

**Enable Automatic Startup:**
```bash
# Already enabled if you followed Step 6
sudo systemctl enable meshtasticd
```

**Install Avahi for Android Auto-Discovery:**
```bash
sudo apt install avahi-daemon
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```
This allows Android Meshtastic clients to automatically discover your gateway.

**Monitor System Health:**
```bash
# View current boot logs
sudo journalctl -u meshtasticd -b

# Follow logs in real-time
sudo journalctl -u meshtasticd -f

# Check for errors
sudo journalctl -u meshtasticd -p err
```

**Alternative Installation Methods:**
- **Docker:** For containerized deployments
- **Flatpak:** For sandboxed applications
- **Fedora:** Via COPR repositories
- **RedHat/CentOS:** Via EPEL repositories

**RNS Integration Note:**
When using Linux native hardware with RNS, you can connect via:
- TCP interface to localhost (if meshtasticd is running)
- Serial/USB passthrough (if configured)
- Direct Python library integration (recommended)

## Configuration

### Step 1: Configure Meshtastic Device

#### Connect to Device
```bash
meshtastic --info
```

#### Set Device Name
```bash
meshtastic --set-owner "YourNodeName"
```

#### Configure LoRa Settings

**Set Region (Required):**
```bash
# Set region according to your location
# Examples: US, EU_868, EU_433, CN, JP, ANZ, KR, TW, RU, IN, NZ_865, TH, UA_868, etc.
meshtastic --set lora.region US
```

**Important:** Setting the correct region is legally required to ensure proper frequency bands and power limits.

**Set Modem Preset:**
```bash
# Available presets (from fastest to slowest):
# - SHORT_TURBO: Fastest, highest bandwidth, lowest airtime, shortest range
# - SHORT_FAST: High speed, moderate range (recommended for RNS if available)
# - SHORT_SLOW: Moderate speed, good range
# - MEDIUM_FAST: Balanced speed and range
# - MEDIUM_SLOW: Good range, moderate speed
# - LONG_FAST: Default - Good balance for most use cases
# - LONG_MODERATE: Better range, slower speed
# - LONG_SLOW: Long range, slow transmission
# - VERY_LONG_SLOW: Maximum range, slowest transmission

# For RNS over Meshtastic, faster presets are recommended:
meshtastic --set lora.modem_preset SHORT_FAST

# Alternative if SHORT_FAST is unavailable:
meshtastic --set lora.modem_preset LONG_FAST
```

**Preset Selection Guidelines:**
- **High-density networks:** Use faster presets (SHORT_TURBO, SHORT_FAST) to reduce congestion
- **Long-range needs:** Use slower presets (LONG_SLOW, VERY_LONG_SLOW) - expect multi-second message delays
- **RNS applications:** Faster presets (SHORT_TURBO or SHORT_FAST) provide better throughput (~500 bytes/s max)
- **Hop limit:** Keep at 3 or lower for most applications

#### Enable Serial Output
```bash
meshtastic --set serial.enabled true
meshtastic --set serial.echo true
```

### Step 2: Configure Reticulum

#### Create Configuration Directory
```bash
# Linux/macOS
mkdir -p ~/.reticulum

# Windows
mkdir %USERPROFILE%\.reticulum
```

#### Create/Edit RNS Configuration File
Create or edit `~/.reticulum/config`:

```ini
[reticulum]
enable_transport = yes
share_instance = yes
shared_instance_port = 37428
instance_control_port = 37429

[logging]
loglevel = 4

[interfaces]
  [[Meshtastic Interface]]
    type = SerialInterface
    port = /dev/ttyUSB0  # Adjust for your system
    speed = 115200
    databits = 8
    parity = none
    stopbits = 1
    enabled = yes
```

#### Find Your Serial Port

**Linux:**
```bash
ls /dev/ttyUSB* /dev/ttyACM*
# or
dmesg | grep tty
```

**macOS:**
```bash
ls /dev/cu.*
```

**Windows:**
Check Device Manager or use:
```powershell
[System.IO.Ports.SerialPort]::getportnames()
```

### Step 3: Set Permissions (Linux Only)
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in for changes to take effect
```

## Testing the Setup

### Step 1: Start Reticulum
```bash
rnsd
```

### Step 2: Check Interface Status
In a new terminal:
```bash
rnstatus
```

You should see your Meshtastic interface listed and showing as active.

### Step 3: Test with Echo Utility
```bash
# On first device
rnsd

# On second device (or another terminal)
# Get the destination hash from rnstatus
echo "Test message" | rncp - <destination_hash>:test.txt
```

### Step 4: Test with Built-in Examples
```bash
# Start a simple echo server
python3 -m RNS.Utilities.rnecho --serve

# From another device, connect to the echo server
python3 -m RNS.Utilities.rnecho <destination_hash>
```

## Troubleshooting

### Device Not Detected
1. Check USB cable (ensure it's a data cable, not charge-only)
2. Verify device is powered on
3. Check permissions (Linux)
4. Try different USB port
5. Update device drivers (Windows)

### RNS Not Starting
1. Check configuration file syntax
2. Verify serial port is correct
3. Ensure no other application is using the serial port
4. Check logs: `tail -f ~/.reticulum/logfile`

### Poor Performance/Connectivity
1. Check LoRa settings (frequency, bandwidth, spreading factor)
2. Verify antenna connection
3. Check for interference
4. Increase TX power (within legal limits)
5. Try different modem presets

### Common Error Messages

**"Could not open serial port"**
- Port is wrong or already in use
- Permission issues (Linux)
- Device not connected

**"Interface failed to start"**
- Configuration error
- Hardware issue
- Firmware incompatibility

## Getting Started with RNS Applications

### NomadNet - Off-Grid Mesh Communication

**What is NomadNet?**
NomadNet is a decentralized messaging and content platform built on Reticulum, offering:
- **Encrypted messaging** with forward secrecy and extreme privacy
- **Zero-configuration** mesh networking (no servers required)
- **Distributed message storage** for offline message delivery
- **Node-hosted pages and files** creating a decentralized web
- **Built-in text browser** for exploring mesh content
- **Works entirely off-grid** - no internet required

**Installation:**
```bash
# Install via pip
pip3 install nomadnet

# Launch NomadNet
nomadnet
```

**First Steps:**
1. Launch nomadnet - you'll receive an integrated getting-started guide
2. Use Ctrl+U to enter node addresses directly
3. Browse the RNS Testnet to discover existing nodes and services
4. Create your own pages using bandwidth-efficient markup

**Use Cases for NomadNet over Meshtastic:**
- **Emergency communication:** Off-grid messaging during disasters
- **Community networks:** Local mesh information sharing
- **Remote areas:** Communication without cellular/internet
- **Privacy-focused:** End-to-end encrypted bulletin boards
- **Digital resilience:** Independent communication infrastructure

**Important Notes:**
- Uses LXMF (Lightweight Extensible Message Format) for messaging
- Messages are stored and forwarded for offline recipients
- Has not been externally security audited
- Works seamlessly across all Reticulum interfaces

**Example Workflow:**
```bash
# Start RNS daemon with Meshtastic interface
rnsd

# In another terminal, launch NomadNet
nomadnet

# Navigate using arrow keys, Ctrl+Q to quit
# Press 'n' for new message, 'c' for conversations
# Use built-in help with '?' key
```

### Reticulum Meshchat - Web-Based GUI

**What is Meshchat?**
A modern web-based communications app for Reticulum with a user-friendly interface:
- **Web GUI** accessible at http://localhost:8000
- **Text messaging** compatible with NomadNet and Sideband
- **File transfers** between peers
- **Audio calls** (beta) using codec2 for low-bandwidth
- **LXMF Propagation Node** hosting for message relay
- **Nomad Network node browsing** and file access

**Installation:**

*Option 1: Standalone Application (Easiest)*
```bash
# Download from GitHub releases page:
# https://github.com/liamcottle/reticulum-meshchat/releases
# Available for Windows, Mac, and Linux
```

*Option 2: Run from Source*
```bash
git clone https://github.com/liamcottle/reticulum-meshchat
cd reticulum-meshchat
pip3 install -r requirements.txt
npm install --omit=dev && npm run build-frontend
python meshchat.py
```

**Usage:**
1. Start RNS daemon: `rnsd`
2. Launch Meshchat: `python meshchat.py`
3. Open browser to `http://localhost:8000`
4. Configure your identity and start messaging

**Why Use Meshchat over Meshtastic?**
- Modern web interface easier for new users
- Real-time messaging focus (vs NomadNet's BBS style)
- Audio call support for voice communication
- Can run on gateway nodes to provide web access to RNS network
- Compatible with other LXMF applications

### Other RNS Applications

**Sideband (Mobile):**
```bash
# For Android: Install from F-Droid or GitHub
# For Linux: pip3 install sbapp
```
Mobile-friendly RNS client with LXMF messaging and location sharing.

**rnsh (Remote Shell):**
```bash
pip3 install rnsh
# Server side: rnsh -l
# Client side: rnsh <destination_hash>
```
Secure remote shell access over RNS for system administration.

## Advanced Features

### Multi-Interface Setup
You can use multiple interfaces simultaneously:

```ini
[interfaces]
  [[Meshtastic Interface]]
    type = SerialInterface
    port = /dev/ttyUSB0
    speed = 115200
    enabled = yes

  [[TCP Interface]]
    type = TCPClientInterface
    target_host = 192.168.1.100
    target_port = 4242
    enabled = yes
```

### Transport Node Configuration
To enable your node as a transport (relay) node:

```ini
[reticulum]
enable_transport = yes
```

### Announce Behavior
Configure how your node announces itself:

```python
# In your Python application
import RNS

identity = RNS.Identity()
destination = RNS.Destination(
    identity,
    RNS.Destination.IN,
    RNS.Destination.SINGLE,
    "example",
    "service"
)

# Announce every 5 minutes
destination.announce()
```

## Security Considerations

### Identity Management
- Keep your identity file secure: `~/.reticulum/identities/`
- Back up your identity regularly
- Use strong encryption for sensitive applications

### Network Security
- RNS provides end-to-end encryption by default
- Each destination has its own cryptographic identity
- Links are authenticated and encrypted

### Physical Security
- Meshtastic devices broadcast openly
- Consider operational security when deploying
- Be aware of radio regulations in your area

## Performance Optimization

### Tuning LoRa Parameters

**Modem Preset Selection:**
- **SHORT_TURBO (8):** 0.4s delay - Fastest, best for RNS (recommended)
- **SHORT_FAST (6):** 1s delay - High speed, good for dense networks
- **SHORT_SLOW (5):** 3s delay - Moderate speed with better range
- **LONG_MODERATE (7):** 12s delay - Long range, moderate speed
- **MEDIUM_FAST (4):** 4s delay - Slowest recommended for RNS
- **MEDIUM_SLOW (3):** 6s delay - Extended range applications
- **LONG_SLOW (1):** 15s delay - Very long range
- **LONG_FAST (0):** 8s delay - Default balanced preset
- **VERY_LONG_SLOW:** Maximum range, multi-second delays

**Technical Parameters:**
- **Long Range:** Higher spreading factor (SF 9-12), lower bandwidth (31-125 kHz)
- **High Speed:** Lower spreading factor (SF 7-8), higher bandwidth (250-500 kHz)
- **Balanced:** LONG_FAST or SHORT_FAST presets

### RNS Configuration
```ini
[interfaces]
  [[Meshtastic Interface]]
    type = SerialInterface
    port = /dev/ttyUSB0
    speed = 115200
    enabled = yes
    # Optional: Limit bitrate
    bitrate = 1200
```

### Packet Size Considerations
- Meshtastic has MTU limitations (~200 bytes)
- RNS automatically fragments larger packets
- Smaller packets = better reliability in poor conditions

### Network Topology
- Deploy transport nodes at high points
- Use directional antennas for point-to-point links
- Consider network density and potential congestion

## References

### Official Documentation
- [Reticulum Documentation](https://reticulum.network/manual/)
- [Meshtastic Documentation](https://meshtastic.org/docs/)
- [RNS GitHub Repository](https://github.com/markqvist/Reticulum)
- [Meshtastic GitHub Repository](https://github.com/meshtastic/firmware)

### Community Resources
- [Reticulum Discussion Forum](https://github.com/markqvist/Reticulum/discussions)
- [Meshtastic Discord](https://discord.com/invite/ktMAKGBnBs)
- [Meshtastic Forum](https://meshtastic.discourse.group/)

### RNS Applications and Utilities

**Core Utilities (Included with RNS):**
- **rnsd:** RNS daemon/service
- **rnstatus:** Monitor interface status and network statistics
- **rnpath:** Discover and display routes to destinations
- **rnprobe:** Test connectivity to destinations
- **rncp:** File transfer utility (recommended for Meshtastic)
- **rnx:** Execute commands on remote nodes

**Advanced Applications:**
- **rnsh:** Remote shell over RNS - secure terminal access
- **nomadnet:** Full-featured mesh communication system with BBS
- **sideband:** Mobile-friendly RNS application for Android/Linux
- **lxmf:** Lightweight message format for asynchronous messaging

**Example Usage:**
```bash
# File transfer over Meshtastic
rncp local_file.txt <destination_hash>:remote_file.txt

# Check network status
rnstatus

# Discover path to destination
rnpath <destination_hash>

# Remote shell access
rnsh <destination_hash>
```

### Radio Regulations
- Consult your local regulations for LoRa frequency usage
- Respect duty cycle limitations
- Use appropriate transmit power levels
- [FCC Part 15 (US)](https://www.fcc.gov/wireless/bureau-divisions/mobility-division/rules-regulations-title-47)
- [ETSI EN 300 220 (EU)](https://www.etsi.org/deliver/etsi_en/300200_300299/30022001/03.01.01_60/en_30022001v030101p.pdf)

---

## Quick Start Checklist

- [ ] Install Python 3.7+
- [ ] Install RNS: `pip3 install rns`
- [ ] Install Meshtastic: `pip3 install meshtastic`
- [ ] Flash Meshtastic firmware to device
- [ ] Configure Meshtastic device (region, modem preset)
- [ ] Find serial port for device
- [ ] Create RNS config file with Meshtastic interface
- [ ] Set permissions (Linux only)
- [ ] Start rnsd
- [ ] Check status with rnstatus
- [ ] Test with echo or other utilities

## Need Help?

If you encounter issues not covered in this guide:
1. Check the official documentation
2. Review RNS logs: `~/.reticulum/logfile`
3. Ask in the community forums
4. File a bug report if you've found an issue

---

**Last Updated:** December 2024
**Version:** 1.0
**Contributors:** Reticulum and Meshtastic Communities
