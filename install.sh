#!/bin/bash
set -e

echo "Installing modpi to /opt/modpi"

# Install dependencies
echo "Installing dependencies..."
sudo apt update
sudo apt install -y git python3-luma.oled python3-smbus python3-psutil

# Create modpi user if it doesn't exist
if ! id "modpi" &>/dev/null; then
    echo "Creating modpi user..."
    sudo useradd -r -s /bin/false -d /opt/modpi modpi
fi

# Clone or update repository
if [[ ! -d /opt/modpi/.git ]]; then
    echo "Cloning modpi repository..."
    sudo -u modpi git clone https://github.com/codesmax/modpi.git /opt/modpi
else
    echo "Repository already exists, updating..."
    sudo -u modpi git -C /opt/modpi pull
fi

# Install systemd service files
echo "Installing systemd services..."
sudo cp /opt/modpi/services/*.service /etc/systemd/system/

# Reload systemd and enable services
echo "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable exp-config-startup.service
sudo systemctl enable exp-config-shutdown.service
sudo systemctl enable oled-stats.service
sudo systemctl start exp-config-startup.service
sudo systemctl start oled-stats.service

echo ""
echo "✅ Installation complete!"
echo ""
echo "Services installed:"
echo "  - exp-config-startup.service (enabled, started)"
echo "  - exp-config-shutdown.service (enabled)"
echo "  - oled-stats.service (enabled, started)"
echo ""
echo "Check status with:"
echo "  sudo systemctl status oled-stats.service"
echo "  sudo systemctl status exp-config-startup.service"
echo ""
echo "View logs with:"
echo "  sudo journalctl -u modpi -f"
