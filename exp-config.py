from expansion import Expansion
import argparse
import sys

def list_config(exp):
    """Display expansion board configuration"""
    print(f"Brand:          {exp.get_brand()}")
    print(f"Version:        {exp.get_version()}")
    print(f"I2C Address:    0x{exp.get_i2c_addr():02X}")
    print(f"LED Colors:     RGB{exp.get_all_led_color()}")
    print(f"LED Mode:       {exp.get_led_mode()}")
    print(f"Fan Mode:       {exp.get_fan_mode()}")
    print(f"Fan Frequency:  {exp.get_fan_frequency()} Hz")
    print(f"Fan0 Duty:      {exp.get_fan0_duty()}")
    print(f"Fan1 Duty:      {exp.get_fan1_duty()}")
    print(f"Fan Threshold:  {exp.get_fan_threshold()}")
    print(f"Board Temp:     {exp.get_temp()}°C")

def reset_config(exp):
    """Reset expansion board to default configuration"""
    print("⚙️  Resetting expansion board to defaults...", end="")
    exp.set_i2c_addr(exp.I2C_ADDRESS)
    exp.set_led_mode(4)
    exp.set_all_led_color(255, 255, 255)
    exp.set_fan_mode(2)
    exp.set_fan_frequency(50)
    exp.set_fan_duty(0, 0)
    exp.set_fan_threshold(30, 45)
    exp.set_power_on_check(1)
    exp.set_save_flash(1)
    print("DONE")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configure Freenove expansion board')
    parser.add_argument('--list', action='store_true', help='Display current configuration')
    parser.add_argument('--reset', action='store_true', help='Reset to default configuration')
    parser.add_argument('--save', action='store_true', help='Save configuration to flash')
    parser.add_argument('--i2c-addr', type=lambda x: int(x, 0), metavar='ADDR', help='I2C address (hex or decimal)')
    parser.add_argument('--led-mode', type=int, choices=[1, 2, 3, 4], metavar='MODE', help='LED mode: 1=RGB, 2=following, 3=breathing, 4=rainbow')
    parser.add_argument('--led-color', metavar='R,G,B', help='LED color as R,G,B (0-255)')
    parser.add_argument('--fan-mode', type=int, choices=[1, 2], metavar='MODE', help='Fan mode: 1=manual, 2=auto')
    parser.add_argument('--fan-frequency', type=int, metavar='HZ', help='Fan PWM frequency in Hz')
    parser.add_argument('--fan-duty', metavar='D0,D1', help='Fan duty cycles as D0,D1 (0-255)')
    parser.add_argument('--fan-threshold', metavar='LOW,HIGH', help='Fan temperature thresholds as LOW,HIGH (°C)')
    parser.add_argument('--power-on-check', type=int, choices=[0, 1], metavar='STATE', help='Power-on check: 0=disable, 1=enable')

    args = parser.parse_args()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    exp = Expansion()
    try:
        if args.list:
            list_config(exp)
        elif args.reset:
            reset_config(exp)
        else:
            settings_changed = False

            if args.i2c_addr is not None:
                exp.set_i2c_addr(args.i2c_addr)
                settings_changed = True

            if args.led_mode is not None:
                exp.set_led_mode(args.led_mode)
                settings_changed = True

            if args.led_color is not None:
                r, g, b = map(int, args.led_color.split(','))
                exp.set_all_led_color(r, g, b)
                settings_changed = True

            if args.fan_mode is not None:
                exp.set_fan_mode(args.fan_mode)
                settings_changed = True

            if args.fan_frequency is not None:
                exp.set_fan_frequency(args.fan_frequency)
                settings_changed = True

            if args.fan_duty is not None:
                d0, d1 = map(int, args.fan_duty.split(','))
                exp.set_fan_duty(d0, d1)
                settings_changed = True

            if args.fan_threshold is not None:
                low, high = map(int, args.fan_threshold.split(','))
                exp.set_fan_threshold(low, high)
                settings_changed = True

            if args.power_on_check is not None:
                exp.set_power_on_check(args.power_on_check)
                settings_changed = True

            if settings_changed:
                print("⚙️  Configuration updated")
                if args.save:
                    exp.set_save_flash(1)
                    print("⚙️  Configuration saved to flash")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        exp.end()
