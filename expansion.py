# Freenove expansion board Python library
# Modified from original at https://github.com/Freenove/Freenove_Computer_Case_Kit_for_Raspberry_Pi/blob/main/Code/expansion.py
import smbus

class Expansion:
    I2C_ADDRESS = 0x21
    REG_I2C_ADDRESS = 0x00        # Set I2C address
    REG_LED_SPECIFIED = 0x01      # Set specified LED color
    REG_LED_ALL = 0x02            # Set all LEDs color
    REG_LED_MODE = 0x03           # Set LED running mode
    REG_FAN_MODE = 0x04           # Set fan running mode
    REG_FAN_FREQUENCY = 0x05      # Set fan frequency
    REG_FAN_DUTY = 0x06           # Set fan duty cycle
    REG_FAN_THRESHOLD = 0x07      # Set fan temperature threshold
    REG_POWER_ON_CHECK = 0x08     # Set power-on check
    REG_SAVE_FLASH = 0xff         # Save to flash

    REG_I2C_ADDRESS_READ = 0xf3   # Read I2C address
    REG_LED_SPECIFIED_READ = 0xf4 # Read specified LED color
    REG_LED_ALL_READ = 0xf5       # Read all LEDs color
    REG_LED_MODE_READ = 0xf6      # Read LED mode
    REG_FAN_MODE_READ = 0xf7      # Read fan mode
    REG_FAN_FREQUENCY_READ = 0xf8 # Read fan frequency
    REG_FAN0_DUTY_READ = 0xf9     # Read fan duty cycle 1 value
    REG_FAN1_DUTY_READ = 0xfa     # Read fan duty cycle 2 value
    REG_FAN_THRESHOLD_READ = 0xfb # Read fan temperature threshold
    REG_TEMP_READ = 0xfc          # Read temperature value
    REG_BRAND = 0xfd              # Read brand
    REG_VERSION = 0xfe            # Read version

    def __init__(self, bus_number=1, address=I2C_ADDRESS):
        # Initialize I2C bus and address
        self.bus_number = bus_number
        self.bus = smbus.SMBus(self.bus_number)
        self.address = address

    def write(self, reg, values):
        # Write data to I2C register
        try:
            if isinstance(values, list):
                self.bus.write_i2c_block_data(self.address, reg, values)
            else:
                self.bus.write_byte_data(self.address, reg, values)
        except IOError as e:
            print("Error writing to I2C bus:", e)

    def read(self, reg, length=1):
        # Read data from I2C register
        if length == 1:
            return self.bus.read_byte_data(self.address, reg)
        else:
            return self.bus.read_i2c_block_data(self.address, reg, length)

    def end(self):
        # Close I2C bus
        self.bus.close()

    def set_i2c_addr(self, addr):
        # Set I2C address
        self.address = addr
        self.write(self.REG_I2C_ADDRESS, addr)

    def set_led_color(self, led_id, r, g, b):
        # Set color for specified LED
        cmd = [led_id, r, g, b]
        self.write(self.REG_LED_SPECIFIED, cmd)

    def set_all_led_color(self, r, g, b):
        # Set color for all LEDs
        cmd = [r, g, b]
        self.write(self.REG_LED_ALL, cmd)

    def set_led_mode(self, mode):
        # Set LED running mode
        self.write(self.REG_LED_MODE, mode)

    def set_fan_mode(self, mode):
        # Set fan running mode
        self.write(self.REG_FAN_MODE, mode)

    def set_fan_frequency(self, freq):
        # Set fan frequency
        frequency = [
            (freq >> 24) & 0xFF,
            (freq >> 16) & 0xFF,
            (freq >> 8) & 0xFF,
            freq & 0xFF
        ]
        self.write(self.REG_FAN_FREQUENCY, frequency)

    def set_fan_duty(self, duty0, duty1):
        # Set fan duty cycle
        duty = [duty0, duty1]
        self.write(self.REG_FAN_DUTY, duty)

    def set_fan_threshold(self, low_threshold, high_threshold):
        # Set fan temperature threshold
        threshold = [low_threshold, high_threshold]
        self.write(self.REG_FAN_THRESHOLD, threshold)

    def set_power_on_check(self, state):
        # Set power-on check state
        self.write(self.REG_POWER_ON_CHECK, state)

    def set_save_flash(self, state):
        # Save configuration to flash
        self.write(self.REG_SAVE_FLASH, state)

    def get_i2c_addr(self):
        # Get I2C address
        return self.read(self.REG_I2C_ADDRESS_READ)

    def get_led_color(self, led_id):
        # Get color for specified LED
        cmd = [led_id]
        self.write(self.REG_LED_SPECIFIED, cmd)
        return self.read(self.REG_LED_SPECIFIED_READ, 3)

    def get_all_led_color(self):
        # Get color for all LEDs
        return self.read(self.REG_LED_ALL_READ, 12)

    def get_led_mode(self):
        # Get LED running mode
        return self.read(self.REG_LED_MODE_READ)

    def get_fan_mode(self):
        # Get fan running mode
        return self.read(self.REG_FAN_MODE_READ)

    def get_fan_frequency(self):
        # Get fan frequency
        arr = self.read(self.REG_FAN_FREQUENCY_READ, 4)
        freq = (arr[0] << 24) | (arr[1] << 16) | (arr[2] << 8) | arr[3];
        return freq

    def get_fan0_duty(self):
        # Get fan duty cycle 1 value
        return self.read(self.REG_FAN0_DUTY_READ)

    def get_fan1_duty(self):
        # Get fan duty cycle 2 value
        return self.read(self.REG_FAN1_DUTY_READ)

    def get_fan_threshold(self):
        # Get fan temperature threshold
        return self.read(self.REG_FAN_THRESHOLD_READ, 2)

    def get_temp(self):
        # Get temperature value
        return self.read(self.REG_TEMP_READ)

    def get_brand(self):
        # Get brand information
        brand_bytes = self.read(self.REG_BRAND, 9)
        return ''.join(chr(b) for b in brand_bytes).rstrip('\x00')

    def get_version(self):
        # Get version information
        version_bytes = self.read(self.REG_VERSION, 14)
        return ''.join(chr(b) for b in version_bytes).rstrip('\x00')
