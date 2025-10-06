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
    sudo useradd -r -s /bin/false -d /opt/modpi -G i2c modpi
else
    # Ensure existing user is in i2c group
    sudo usermod -a -G i2c modpi
fi

# Create installation directory
echo "Setting up installation directory..."
if [[ ! -d /opt/modpi ]]; then
    sudo mkdir -p /opt/modpi
    sudo chown modpi:modpi /opt/modpi
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

cat <<EOF

✅ Installation complete!

Services installed:
  - exp-config-startup.service (enabled, started)
  - exp-config-shutdown.service (enabled)
  - oled-stats.service (enabled, started)

Check status with:
  sudo systemctl status oled-stats.service
  sudo systemctl status exp-config-startup.service
  sudo systemctl status exp-config-shutdown.service

View logs with:
  sudo journalctl -u exp-config-startup.service -f
  sudo journalctl -u exp-config-shutdown.service -f
  sudo journalctl -u oled-stats.service -f

EOF
