# modpi

Scripts and utilities for a modded Raspberry Pi with Freenove expansion board.

## What's included

- **expansion.py** - Python library for Freenove expansion board (I2C control of LEDs, fans, temp sensor)
- **exp-config.py** - CLI tool to configure expansion board settings
- **oled-stats.py** - Real-time system stats display on 128x64 OLED (CPU, memory, network, temps, fan, uptime)

## Hardware

- Raspberry Pi (tested on Pi 5)
- Freenove expansion board
- 128x64 SSD1306 OLED display (I2C)

## Installation

One-line install (clones repo to `/opt/modpi`, sets up systemd services):

```bash
curl -sSL https://raw.githubusercontent.com/codesmax/modpi/main/install.sh | bash
```

## Usage

```bash
# Configure expansion board
python3 exp-config.py --led-mode 4 --fan-threshold 45,60 --save

# List current settings
python3 exp-config.py --list

# Reset to defaults
python3 exp-config.py --reset

# Run stats display manually
python3 oled-stats.py
```

Services auto-start on boot. View logs: `sudo journalctl -u oled-stats -f`
