#!/usr/bin/env python
# -*- coding: utf8 -*-
import time
import pyA20.gpio.gpio as GPIO
import pyA20.gpio.port as PORT
import pyA20.spi as spi
import Image, ImageDraw, ImageFont
# Constants
SSD1306_I2C_ADDRESS = 0x3C    # 011110+SA0+RW - 0x3C or 0x3D
SSD1306_SETCONTRAST = 0x81
SSD1306_DISPLAYALLON_RESUME = 0xA4
SSD1306_DISPLAYALLON = 0xA5
SSD1306_NORMALDISPLAY = 0xA6
SSD1306_INVERTDISPLAY = 0xA7
SSD1306_DISPLAYOFF = 0xAE
SSD1306_DISPLAYON = 0xAF
SSD1306_SETDISPLAYOFFSET = 0xD3
SSD1306_SETCOMPINS = 0xDA
SSD1306_SETVCOMDETECT = 0xDB
SSD1306_SETDISPLAYCLOCKDIV = 0xD5
SSD1306_SETPRECHARGE = 0xD9
SSD1306_SETMULTIPLEX = 0xA8
SSD1306_SETLOWCOLUMN = 0x00
SSD1306_SETHIGHCOLUMN = 0x10
SSD1306_SETSTARTLINE = 0x40
SSD1306_MEMORYMODE = 0x20
SSD1306_COLUMNADDR = 0x21
SSD1306_PAGEADDR = 0x22
SSD1306_COMSCANINC = 0xC0
SSD1306_COMSCANDEC = 0xC8
SSD1306_SEGREMAP = 0xA0
SSD1306_CHARGEPUMP = 0x8D
SSD1306_EXTERNALVCC = 0x1
SSD1306_SWITCHCAPVCC = 0x2

# Scrolling constants
SSD1306_ACTIVATE_SCROLL = 0x2F
SSD1306_DEACTIVATE_SCROLL = 0x2E
SSD1306_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1306_RIGHT_HORIZONTAL_SCROLL = 0x26
SSD1306_LEFT_HORIZONTAL_SCROLL = 0x27
SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL = 0x2A
NRSTPD = PORT.PC7
DC_SEL = PORT.PC3

class OLED: 
    x=0
    def __init__(self):
        GPIO.init()
        GPIO.setcfg(NRSTPD, GPIO.OUTPUT)
        GPIO.setcfg(DC_SEL, GPIO.OUTPUT)
        self.width = 128
        self.height = 64
        self._pages = self.height // 8
        self._buffer = [0]* (self.width * self._pages)
        self._vccstate = SSD1306_SWITCHCAPVCC
        spi.open('/dev/spidev0.0', mode=0, delay=0, bits_per_word=8, speed=15000000)
        # 128x32 pixel specific initialization.
        self.x = 0
        self.y = 0

    def _initialize(self):

        # 128x64 pixel specific initialization.
        self.command(SSD1306_DISPLAYOFF)  # 0xAE
        self.command(SSD1306_SETDISPLAYCLOCKDIV)  # 0xD5
        self.command(0x80)  # the suggested ratio 0x80
        self.command(SSD1306_SETMULTIPLEX)  # 0xA8
        self.command(0x3F)
        self.command(SSD1306_SETDISPLAYOFFSET)  # 0xD3
        self.command(0x0)  # no offset
        self.command(SSD1306_SETSTARTLINE | 0x0)  # line #0
        self.command(SSD1306_CHARGEPUMP)  # 0x8D
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x10)
        else:
            self.command(0x14)
        self.command(SSD1306_MEMORYMODE)  # 0x20
        self.command(0x00)  # 0x0 act like ks0108
        self.command(SSD1306_SEGREMAP | 0x1)
        self.command(SSD1306_COMSCANDEC)
        self.command(SSD1306_SETCOMPINS)  # 0xDA
        self.command(0x12)
        self.command(SSD1306_SETCONTRAST)  # 0x81
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x9F)
        else:
            self.command(0xCF)
        self.command(SSD1306_SETPRECHARGE)  # 0xd9
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x22)
        else:
            self.command(0xF1)
        self.command(SSD1306_SETVCOMDETECT)  # 0xDB
        self.command(0x40)
        self.command(SSD1306_DISPLAYALLON_RESUME)  # 0xA4
        self.command(SSD1306_NORMALDISPLAY)  # 0xA6
    def reset(self):
        """Reset the display."""

        # Set reset high for a millisecond.
        GPIO.output(NRSTPD, 1)
        time.sleep(0.001)
        # Set reset low for 10 milliseconds.
        GPIO.output(NRSTPD, 0)
        time.sleep(0.010)
        # Set reset high again.
        GPIO.output(NRSTPD, 1)

    def display(self):
        """Write display buffer to physical display."""
        self.command(SSD1306_COLUMNADDR)
        self.command(0)              # Column start address. (0 = reset)
        self.command(self.width-1)   # Column end address.
        self.command(SSD1306_PAGEADDR)
        self.command(0)              # Page start address. (0 = reset)
        self.command(self._pages-1)  # Page end address.
        # Write buffer data.
        # Set DC high for data.
        GPIO.output(DC_SEL, 1)
        # Write buffer.
        #print self._buffer
        spi.write(self._buffer)

    def begin(self, vccstate=SSD1306_SWITCHCAPVCC):
        """Initialize display."""
        self._vccstate = vccstate
        # Reset and initialize display.
        self.reset()
        self._initialize()
        # Turn on the display.
        self.command(SSD1306_DISPLAYON)
        
    def data(self, c):
        """Send byte of data to display."""
        GPIO.output(self.DC_SEL, 1)
        spi.write([c])

    def command(self, c):
        """Send command byte to display."""
        GPIO.output(DC_SEL, 0)
        spi.write([c])

    def image(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                             .format(self.width, self.height))
        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        # Iterate through the memory pages
        index = 0
        for page in range(self._pages):
            # Iterate through all x axis columns.
            for x in range(self.width):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= 0 if pix[(x, page * 8 + 7 - bit)] == 0 else 1
                # Update buffer byte and increment to next byte.
                self._buffer[index] = bits
                index += 1

    def clear(self):
        """Clear contents of image buffer."""
        self._buffer = [0] * (self.width * self._pages)
    def draw(self):
        #self.clear()
        tmp = self.x
        tmpx = tmp-1
        tmplen = 0
        if tmpx < 0:
            tmpx = 127

        while tmp < 8*128:
            self._buffer[tmpx] = 0
            if tmp < 128:
                tmplen = 0xff << random.randint(0, 7)
            elif tmp > 7*128:

                tmplen = 0xff >> random.randint(0, 7)
            else:
                tmplen = 0xff
            self._buffer[tmp] =tmplen
            tmp = tmp+128
            tmpx = tmpx+128

        self.x = self.x+1
        if self.x >= 128:
            self.x = 0
    def test(self):

        self._buffer[128 * 3 + 15] = 0xff>>1

    def image(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                             .format(self.width, self.height))
        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        # Iterate through the memory pages
        index = 0
        #print pix
        for page in range(self._pages):
            # Iterate through all x axis columns.
            for x in range(self.width):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= 0 if pix[(x, page * 8 + 7 - bit)] == 0 else 1
                # Update buffer byte and increment to next byte.
                self._buffer[index] = bits
                index += 1
