# RNS Over Meshtastic Gateway

A Reticulum Network Stack (RNS) interface that enables secure, encrypted communication over Meshtastic networks. This project bridges RNS applications with existing Meshtastic hardware, allowing you to leverage mesh radio infrastructure for off-grid data transfer and communication.

Built as an improved successor to the Meshtastic File Transfer project, this gateway provides reliable file transfers using RNS's rncp utility and supports all RNS-based applications like NomadNet and Sideband. While transfer speeds reach approximately 500 bytes/s (slower than dedicated RNodes), the system seamlessly integrates with existing Meshtastic networks and can operate alongside standard Meshtastic nodes.

This solution is ideal for creating dedicated data channels on Meshtastic networks, enabling more intensive applications like secure messaging, file sharing, and off-grid services without disrupting regular Meshtastic traffic.

## Quick Start (Recommended)

Use the interactive installer for easy setup:

```bash
# Run the installer
python3 install.py
```

The installer will guide you through:
- ✓ Installing required packages (RNS, Meshtastic, pyserial)
- ✓ Detecting and configuring your Meshtastic device
- ✓ Setting up the RNS interface
- ✓ Optional: Installing RNS applications (NomadNet, rnsh, Sideband)

## Manual Installation
- Install Meshtastic Python Library
- Add the file [Meshtastic_Interface.py](Interface%2FMeshtastic_Interface.py) to your interfaces folder for reticulum
- Modify the node config file and add the following
```
 [[Meshtastic Interface]]
  type = Meshtastic_Interface
  enabled = true
  mode = gateway
  port = /dev/[path to device]  # Optional: Meshtastic serial device port
  ble_port = short_1234  # Optional: Meshtastic BLE device ID (Replacement for serial port)
  tcp_port = 127.0.0.1:4403  #Optional: Meshtastic TCP IP. [port is optional if using default port] (Replacement for serial or ble)
  data_speed = 8  # Radio speed setting desired for the network(do not use long-fast)
```

- Radio settings and their associated transfer speeds are shown below; time unit is seconds between packets (from [Meshtastic_Interface.py](Interface%2FMeshtastic_Interface.py))
```python
speed_to_delay = {8: .4,  # Short-range Turbo (recommended)
                  6: 1,  # Short Fast (best if short turbo is unavailable)
                  5: 3,  # Short-range Slow (best if short turbo is unavailable)
                  7: 12,  # Long Range - moderate Fast
                  4: 4,  # Medium Range - Fast  (Slowest recommended speed)
                  3:6,  # Medium Range - Slow
                  1: 15,  # Long Range - Slow
                  0: 8  # Long Range - Fast
                  }
```
- Use the number on the left to set the speed and change the number on the right to change the max transmission rate from the radio
