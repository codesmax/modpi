# -*- coding: utf-8 -*-

from expansion import Expansion
import argparse

def set_config(exp):
    """Update expansion board configuration"""
    print("⚙️  Updating expansion board configuration...\r", end="")
    exp.set_i2c_addr(exp.I2C_ADDRESS)   # I2C address (Default: 0x21)
    exp.set_all_led_color(255,255,255)  # LED RGB colors: 0-255 (Default: 255,255,255)
    exp.set_led_mode(4)                 # LED display mode: 1 = RGB, 2 = following, 3 = breathing, 4 = rainbow (Default: 4)
    exp.set_fan_mode(2)                 # Fan control mode: 1 = manual, 2 = auto (Default: 2)
    exp.set_fan_duty(0, 0)              # Fan0 and Fan1 duty cycle: 0-255 (Default: 0,0)
    exp.set_fan_threshold(45, 60)       # Fan lower + upper temperature threshold: 45-60°C (Default: 30,45)
    exp.set_power_on_check(1)           # Power-on check: 1 = enable, 0 = disable (Default: 1)
    exp.set_save_flash(1)               # Save to flash: 1 = enable, 0 = disable
    print("DONE")

def get_config(exp):
    """Display expansion board configuration"""
    print("⚙️  Expansion Board Configuration")
    print(f"\tBrand:          {exp.get_brand()}")
    print(f"\tVersion:        {exp.get_version()}")
    print(f"\tI2C Address:    0x{exp.get_i2c_addr():02X}")
    print(f"\tLED Colors:     RGB{exp.get_all_led_color()}")
    print(f"\tLED Mode:       {exp.get_led_mode()}")
    print(f"\tFan Mode:       {exp.get_fan_mode()}")
    print(f"\tFan Frequency:  {exp.get_fan_frequency()}")
    print(f"\tFan0 Duty:      {exp.get_fan0_duty()}")
    print(f"\tFan1 Duty:      {exp.get_fan1_duty()}")
    print(f"\tFan Threshold:  {exp.get_fan_threshold()}")
    print(f"\tBoard Temp:     {exp.get_temp()}°C")
    print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configure Freenove expansion board')
    parser.add_argument('-s', '--set', action='store_true', help='Update configuration settings')
    parser.add_argument('-g', '--get', action='store_true', help='Display current configuration')

    args = parser.parse_args()

    if not args.set and not args.get:
        parser.print_help()
        exit(0)

    exp = Expansion()
    try:
        if args.set:
            set_config(exp)
        if args.get:
            get_config(exp)
    except Exception as e:
        print("Error:", e)
    finally:
        exp.end()
