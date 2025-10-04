import sys
import time
import argparse
import psutil
from psutil._common import bytes2human

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

from expansion import Expansion

class OLEDStats:
    def __init__(self, refresh_interval=1):
        self.refresh_interval = refresh_interval
        self.expansion = None
        self.device = None
        self.font = None
        self.icon_font = None

        # Display dimensions
        self.width = 128
        self.height = 64

        # Layout configuration
        self.padding = 2
        self.icon_width = 16
        self.line_height = 16

        # Font Awesome 7 icon codepoints
        self.ICON_CPU = '\uf2db'
        self.ICON_MEMORY = '\uf538'
        self.ICON_NETWORK = '\uf6ff'
        self.ICON_TEMP = '\uf2c9'
        self.ICON_DOWN = '\uf063'
        self.ICON_UP = '\uf062'

        # Network traffic tracking
        self.prev_net = None

        try:
            # Initialize OLED display
            serial = i2c(port=1, address=0x3C)
            self.device = ssd1306(serial)

            # Load fonts
            self.font = ImageFont.load_default()
            self.icon_font = ImageFont.truetype('fa7-solid-900.otf', 12)

            # Initialize expansion board
            self.expansion = Expansion()

            # Initialize network counters
            self.prev_net = psutil.net_io_counters()
        except Exception as e:
            print(f"Initialization error: {e}")
            sys.exit(1)

    def monitor(self):
        while True:
            try:
                # CPU and memory stats
                cpu_usage = psutil.cpu_percent(interval=0.1)
                mem_usage = psutil.virtual_memory().percent

                # Temperature stats
                cpu_temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
                board_temp = self.expansion.get_temp()

                # Calculate network transfer rates
                curr_net = psutil.net_io_counters()
                bytes_recv = curr_net.bytes_recv - self.prev_net.bytes_recv
                bytes_sent = curr_net.bytes_sent - self.prev_net.bytes_sent
                recv_rate = bytes_recv / self.refresh_interval
                sent_rate = bytes_sent / self.refresh_interval
                self.prev_net = curr_net

                # Format network speeds
                recv_str = bytes2human(recv_rate)
                sent_str = bytes2human(sent_rate)

                # Draw to OLED
                with canvas(self.device) as draw:
                    # Computed positions
                    line1_y = 0
                    line2_y = self.line_height
                    line3_y = self.line_height * 2
                    mid_x = self.width // 2

                    # Line 1: CPU and Memory
                    draw.text((0, line1_y), self.ICON_CPU, font=self.icon_font, fill="white")
                    draw.text((self.icon_width, line1_y + self.padding), f"{cpu_usage:.1f}%", font=self.font, fill="white")
                    draw.text((mid_x - 8, line1_y), self.ICON_MEMORY, font=self.icon_font, fill="white")
                    draw.text((mid_x + 8, line1_y + self.padding), f"{mem_usage:.1f}%", font=self.font, fill="white")

                    # Line 2: Network
                    draw.text((0, line2_y), self.ICON_NETWORK, font=self.icon_font, fill="white")
                    draw.text((self.icon_width, line2_y + self.padding), f"{recv_str}/s", font=self.font, fill="white")
                    draw.text((mid_x - 4, line2_y + self.padding), self.ICON_DOWN, font=self.icon_font, fill="white")
                    draw.text((mid_x + 6, line2_y + self.padding), f"{sent_str}/s", font=self.font, fill="white")
                    draw.text((self.width - 14, line2_y + self.padding), self.ICON_UP, font=self.icon_font, fill="white")

                    # Line 3: Temperature
                    draw.text((0, line3_y), self.ICON_TEMP, font=self.icon_font, fill="white")
                    draw.text((self.icon_width, line3_y + self.padding), f"{cpu_temp:.1f}°C / {board_temp:.1f}°C", font=self.font, fill="white")

                time.sleep(self.refresh_interval)
            except Exception as e:
                print(f"Error monitoring: {e}")
                time.sleep(self.refresh_interval)

    def cleanup(self):
        if self.expansion:
            self.expansion.end()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display Raspberry Pi stats on OLED')
    parser.add_argument('-r', '--refresh', type=float, default=1.0,
                        help='Refresh interval in seconds (default: 1.0)')

    args = parser.parse_args()
    oled_stats = None

    try:
        oled_stats = OLEDStats(refresh_interval=args.refresh)
        oled_stats.monitor()
    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if oled_stats:
            oled_stats.cleanup()
