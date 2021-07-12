#!/usr/bin/python
# coding=utf-8

# Einbindung der notwendigen Grundbibliotheken
import os, sys, time
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
# Einbindung von Bibliotheken für die gewünschten Funktionen
import psutil

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# 128x32 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Alternatively you can specify a software SPI implementation by providing
# digital GPIO pin numbers for all the required display pins.  For example
# on a Raspberry Pi with the 128x32 display you might use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Load default font.
#font = ImageFont.load_default()

# Stardscreen
font = ImageFont.truetype('FreeSans.ttf', 18)
draw.text((1, 0), 'r00t´s SYSMON', font=font, fill=1)
logo = Image.open('rpi.png')
draw.bitmap((0, 20), logo, fill=1)

disp.image(image)
disp.display()
time.sleep(2)

# ----------------------------------------------------------------------------
#  Variablen anlegen
# ----------------------------------------------------------------------------
cpuList = []
scale = 100

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -f 1 -d ' '"
    IP = subprocess.check_output(cmd, shell = True )
    cmd = "free -m | awk 'NR==2{printf \"Mem: %.2f%% frei\", $3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell = True )
    cmd = "vcgencmd measure_temp |cut -f 2 -d '='"
    temp = subprocess.check_output(cmd, shell = True )

    # Write two lines of text.
    font = ImageFont.truetype('FreeSans.ttf', 18)
    draw.text((0, 0), "IP: " + str(IP,'utf-8'), font=font, fill=255)
    font = ImageFont.truetype('FreeSans.ttf', 12)
    draw.text((0, 19), str(MemUsage,'utf-8'), font=font, fill=255)
    draw.text((0, 33), str(Disk,'utf-8'), font=font, fill=255)

    # CPU-Auslastung auslesen
    cpu_val = psutil.cpu_percent(interval=1)

    # Momentanwert anzeigen
    font = ImageFont.truetype('FreeSans.ttf', 11)
    draw.text((1, 48), str(cpu_val) + "%", font=font, fill=255)

    # Werte für Diagramm speichern und Länge auf 110 Einträge begrenzen
    cpuList.append(cpu_val)
    if len(cpuList) > 110:
        cpuList.pop(0)

    # Skalierung des Diagramms
    max_val = max(cpuList)

    if max_val <= 100.0:
        scale = 100
    if max_val <= 90.0:
        scale = 90
    if max_val <= 80.0:
        scale = 80
    if max_val <= 70.0:
        scale = 70
    if max_val <= 60.0:
        scale = 60
    if max_val <= 50.0:
        scale = 50
    if max_val <= 40.0:
        scale = 40    
    if max_val <= 30.0:
        scale = 30
    if max_val <= 20.0:
        scale = 20
    if max_val <= 10.0:
        scale = 10

    # Achsen zeichnen
    draw.line((0, 63, 128, 63), fill=255)    # X
    draw.line((0, 50, 0, 63), fill=255)            # Y
    #draw.line((0, 40, 3, 40), fill=255)            # oberster Skalenwert

    # obersten Y-Wert beschriften
    #draw.text((0, 16), str(scale), font=font, fill=255)

    # X-Koordinate für ersten Wert festlegen
    X = 25

    # Diagrammwerte zeichnen
    for n in range(len(cpuList)):
        Y = float(25 / float(scale) * cpuList[n])
        draw.line((X, 63, X, 63-Y), fill=255)
        X = X + 1

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)
