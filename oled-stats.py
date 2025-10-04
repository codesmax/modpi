import sys
import time
import argparse
import psutil

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

from expansion import Expansion

def format_bytes(num, dp=1):
    """Format bytes to human readable format with configurable decimal places"""
    for unit in ("B", "K", "M", "G", "T"):
        if abs(num) < 1024.0 or unit == "T":
            return f"{round(num)}{unit}" if dp == 0 else f"{num:.{dp}f}{unit}"
        num /= 1024.0

def format_uptime(seconds):
    """Format uptime to most significant unit only"""
    minute = 60
    hour = 60 * minute
    day = 24 * hour
    week = 7 * day
    month = 30 * day
    year = 365 * day

    units = [
        (year, 'y'),
        (month, 'mo'),
        (week, 'w'),
        (day, 'd'),
        (hour, 'h'),
        (minute, 'm'),
        (1, 's')
    ]

    for divisor, suffix in units:
        if seconds >= divisor:
            value = round(seconds / divisor)
            return f"{value}{suffix}"
    return "0s"

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
        self.margin = 2
        self.icon_width = 16
        self.line_height = 16

        # Font Awesome 7 icon codepoints
        self.ICON_CPU = '\uf2db'
        self.ICON_MEMORY = '\uf538'
        self.ICON_NETWORK = '\uf6ff'
        self.ICON_TEMP_CPU = '\uf2c9'
        self.ICON_TEMP_BOARD = '\uf108'
        self.ICON_FAN = '\uf863'
        self.ICON_UPTIME = '\uf017'

        # Network traffic tracking
        self.prev_net = None

        try:
            # Initialize OLED display
            serial = i2c(port=1, address=0x3C)
            self.device = ssd1306(serial)

            # Load fonts
            self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
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
                recv_str = format_bytes(recv_rate, 0)
                sent_str = format_bytes(sent_rate, 0)

                # Fan speed
                fan_speed = psutil.sensors_fans()['pwmfan'][0].current

                # Uptime
                uptime_seconds = time.time() - psutil.boot_time()
                uptime_str = format_uptime(uptime_seconds)

                # Draw to OLED
                # Designed for 4-line display on 128x64 OLED
                with canvas(self.device) as draw:
                    # Computed positions
                    line1_y = self.margin
                    line2_y = self.line_height + self.margin
                    line3_y = self.line_height * 2 + self.margin
                    line4_y = self.line_height * 3 + self.margin
                    mid_x = self.width // 2

                    # X positions for left and right columns
                    left_icon_x = self.margin
                    left_text_x = self.margin + self.icon_width
                    right_icon_x = mid_x + self.margin
                    right_text_x = mid_x + self.margin + self.icon_width

                    # Line 1: CPU and Memory
                    draw.text((left_icon_x, line1_y), self.ICON_CPU, font=self.icon_font, fill="white")
                    draw.text((left_text_x, line1_y), f"{cpu_usage:.1f}%", font=self.font, fill="white")
                    draw.text((right_icon_x, line1_y), self.ICON_MEMORY, font=self.icon_font, fill="white")
                    draw.text((right_text_x, line1_y), f"{mem_usage:.1f}%", font=self.font, fill="white")

                    # Line 2: Network
                    draw.text((left_icon_x, line2_y), self.ICON_NETWORK, font=self.icon_font, fill="white")
                    draw.text((left_text_x, line2_y), f"{recv_str}/s ↓", font=self.font, fill="white")
                    draw.text((right_text_x, line2_y), f"{sent_str}/s ↑", font=self.font, fill="white")

                    # Line 3: Temperature
                    draw.text((left_icon_x, line3_y), self.ICON_TEMP_CPU, font=self.icon_font, fill="white")
                    draw.text((left_text_x, line3_y), f"{cpu_temp:.1f}°C", font=self.font, fill="white")
                    draw.text((right_icon_x, line3_y), self.ICON_TEMP_BOARD, font=self.icon_font, fill="white")
                    draw.text((right_text_x, line3_y), f"{board_temp:.1f}°C", font=self.font, fill="white")

                    # Line 4: Uptime and Fan Speed
                    draw.text((left_icon_x, line4_y), self.ICON_UPTIME, font=self.icon_font, fill="white")
                    draw.text((left_text_x, line4_y), uptime_str, font=self.font, fill="white")
                    draw.text((right_icon_x, line4_y), self.ICON_FAN, font=self.icon_font, fill="white")
                    draw.text((right_text_x, line4_y), f"{fan_speed:.0f}", font=self.font, fill="white")

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
