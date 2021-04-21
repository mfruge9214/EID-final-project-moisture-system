# SPDX-FileCopyrightText: 2017 Dean Miller for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_seesaw.seesaw`
====================================================
An I2C to whatever helper chip.
* Author(s): Dean Miller
Implementation Notes
--------------------
**Hardware:**
* Adafruit `ATSAMD09 Breakout with seesaw
  <https://www.adafruit.com/product/3657>`_ (Product ID: 3657)
**Software and Dependencies:**
* Adafruit CircuitPython firmware: https://circuitpython.org/
* or Adafruit Blinka: https://circuitpython.org/blinka
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

# This code needs to be broken up into analogio, busio, digitalio, and pulseio
# compatible classes so we won't bother with some lints until then.
# pylint: disable=missing-docstring,invalid-name,too-many-public-methods,no-name-in-module

import time

try:
    import struct
except ImportError:
    import ustruct as struct
try:
    from micropython import const
except ImportError:

    def const(x):
        return x


# from adafruit_bus_device.i2c_device import I2CDevice

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_seesaw.git"

_STATUS_BASE = const(0x00)

_GPIO_BASE = const(0x01)
_SERCOM0_BASE = const(0x02)

_TIMER_BASE = const(0x08)
_ADC_BASE = const(0x09)
_DAC_BASE = const(0x0A)
_INTERRUPT_BASE = const(0x0B)
_DAP_BASE = const(0x0C)
_EEPROM_BASE = const(0x0D)
_NEOPIXEL_BASE = const(0x0E)
_TOUCH_BASE = const(0x0F)

_GPIO_DIRSET_BULK = const(0x02)
_GPIO_DIRCLR_BULK = const(0x03)
_GPIO_BULK = const(0x04)
_GPIO_BULK_SET = const(0x05)
_GPIO_BULK_CLR = const(0x06)
_GPIO_BULK_TOGGLE = const(0x07)
_GPIO_INTENSET = const(0x08)
_GPIO_INTENCLR = const(0x09)
_GPIO_INTFLAG = const(0x0A)
_GPIO_PULLENSET = const(0x0B)
_GPIO_PULLENCLR = const(0x0C)

_STATUS_HW_ID = const(0x01)
_STATUS_VERSION = const(0x02)
_STATUS_OPTIONS = const(0x03)
_STATUS_TEMP = const(0x04)
_STATUS_SWRST = const(0x7F)

_TIMER_STATUS = const(0x00)
_TIMER_PWM = const(0x01)
_TIMER_FREQ = const(0x02)

_ADC_STATUS = const(0x00)
_ADC_INTEN = const(0x02)
_ADC_INTENCLR = const(0x03)
_ADC_WINMODE = const(0x04)
_ADC_WINTHRESH = const(0x05)
_ADC_CHANNEL_OFFSET = const(0x07)

_SERCOM_STATUS = const(0x00)
_SERCOM_INTEN = const(0x02)
_SERCOM_INTENCLR = const(0x03)
_SERCOM_BAUD = const(0x04)
_SERCOM_DATA = const(0x05)

_NEOPIXEL_STATUS = const(0x00)
_NEOPIXEL_PIN = const(0x01)
_NEOPIXEL_SPEED = const(0x02)
_NEOPIXEL_BUF_LENGTH = const(0x03)
_NEOPIXEL_BUF = const(0x04)
_NEOPIXEL_SHOW = const(0x05)

_TOUCH_CHANNEL_OFFSET = const(0x10)

_HW_ID_CODE = const(0x55)
_EEPROM_I2C_ADDR = const(0x3F)

# TODO: update when we get real PID
_CRICKIT_PID = const(9999)
_ROBOHATMM1_PID = const(9998)


class Seesaw:
    """Driver for Seesaw i2c generic conversion trip
    :param ~busio.I2C i2c_bus: Bus the SeeSaw is connected to
    :param int addr: I2C address of the SeeSaw device
    :param ~digitalio.DigitalInOut drdy: Pin connected to SeeSaw's 'ready' output"""

    INPUT = const(0x00)
    OUTPUT = const(0x01)
    INPUT_PULLUP = const(0x02)
    INPUT_PULLDOWN = const(0x03)

    def __init__(self, i2c_bus, addr=0x49, drdy=None):
        self._drdy = drdy
        self.addr = addr
        self.i2c_device = i2c_bus
        self.sw_reset()
        

    def sw_reset(self):
        """Trigger a software reset of the SeeSaw chip"""
        self.write8(_STATUS_BASE, _STATUS_SWRST, 0xFF)
        time.sleep(0.500)

        chip_id = self.read8(_STATUS_BASE, _STATUS_HW_ID)

        if chip_id != _HW_ID_CODE:
            print(
                "Seesaw hardware ID returned (0x{:x}) is not "
                "correct! Expected 0x{:x}. Please check your wiring.".format(
                    chip_id, _HW_ID_CODE
                )
            )

    def get_options(self):
        """Retrieve the 'options' word from the SeeSaw board"""
        buf = bytearray(4)
        self.read(_STATUS_BASE, _STATUS_OPTIONS, buf)
        ret = struct.unpack(">I", buf)[0]
        return ret

    def get_version(self):
        """Retrieve the 'version' word from the SeeSaw board"""
        buf = bytearray(4)
        self.read(_STATUS_BASE, _STATUS_VERSION, buf)
        ret = struct.unpack(">I", buf)[0]
        return ret

    def moisture_read(self):
        """Read the value of the moisture sensor"""
        buf = bytearray(2)

        self.read(_TOUCH_BASE, _TOUCH_CHANNEL_OFFSET, buf, 0.005)
        ret = struct.unpack(">H", buf)[0]
        time.sleep(0.001)

        # retry if reading was bad
        count = 0
        while ret > 4095:
            self.read(_TOUCH_BASE, _TOUCH_CHANNEL_OFFSET, buf, 0.005)
            ret = struct.unpack(">H", buf)[0]
            time.sleep(0.001)
            count += 1
            if count > 3:
                raise RuntimeError("Could not get a valid moisture reading.")

        return ret

    def get_temp(self):
        """Read the temperature"""
        buf = bytearray(4)
        self.read(_STATUS_BASE, _STATUS_TEMP, buf, 0.005, length=4)
        buf[0] = buf[0] & 0x3F
        ret = struct.unpack(">I", buf)[0]
        return 0.00001525878 * ret

    def get_i2c_addr(self):
        """Return the device's I2C address stored in its EEPROM"""
        return self.read8(_EEPROM_BASE, _EEPROM_I2C_ADDR)

    def eeprom_write8(self, addr, val):
        """Write a single byte directly to the device's EEPROM"""
        self.eeprom_write(addr, bytearray([val]))

    def eeprom_write(self, addr, buf):
        """Write multiple bytes directly to the device's EEPROM"""
        self.write(_EEPROM_BASE, addr, buf)

    def eeprom_read8(self, addr):
        """Read a single byte directly to the device's EEPROM"""
        return self.read8(_EEPROM_BASE, addr)

    def uart_set_baud(self, baud):
        """Set the serial baudrate of the device"""
        cmd = struct.pack(">I", baud)
        self.write(_SERCOM0_BASE, _SERCOM_BAUD, cmd)

    def write8(self, reg_base, reg, value):
        """Write an arbitrary I2C byte register on the device"""
        self.write(reg_base, reg, bytearray([value]))

    def read8(self, reg_base, reg):
        """Read an arbitrary I2C byte register on the device"""
        ret = bytearray(1)
        self.read(reg_base, reg, ret, length=1)
        return ret[0]

    def read(self, reg_base, reg, buf, delay=0.008, length=2):
        """Read an arbitrary I2C register range on the device"""
        self.write(reg_base, reg)
        time.sleep(delay)
        tmp = self.i2c_device.readfrom(self.addr, length)
        for i in range(length):
            buf[i] = tmp[i]

    def write(self, reg_base, reg, buf=None):
        """Write an arbitrary I2C register range on the device"""
        full_buffer = bytearray([reg_base, reg])
        if buf is not None:
            full_buffer += buf

        self.i2c_device.writeto(self.addr, full_buffer)
