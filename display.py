#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import spidev

import ST7789 as TFT
import datetime
from time import sleep

from PIL import Image, ImageDraw, ImageFont, ImageColor

import numpy as np

import detect
import cv2

import util

# Raspberry Pi pin configuration:
RST = 25
DC  = 24
LED = 19
SPI_PORT = 0
SPI_DEVICE = 0
SPI_MODE = 0b11
SPI_SPEED_HZ = 40000000

# _spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE)
# _spi=SPI.SpiDev(0, 0, max_speed_hz=SPI_SPEED_HZ)
_spi = spidev.SpiDev(SPI_PORT, SPI_DEVICE)
_spi.max_speed_hz=SPI_SPEED_HZ

disp = TFT.ST7789(spi=_spi, mode=SPI_MODE, rst=RST, dc=DC, led=LED)

# Initialize display.
disp.begin()

# Clear display.
disp.clear()

# Analogue clock setting
width = 240
height = 240

# Initial screen
image2 = Image.open('Lum_For_Ants.jpg')
image2.thumbnail((240, 240), Image.ANTIALIAS)
image2 = util.expand2square(image2, (0,0,0))

disp.display(image2)

# font setting
font = ImageFont.load_default()
fontJ = ImageFont.truetype('DejaVuSans.ttf', 16, encoding='unic')

sleep(1)

image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
draw = ImageDraw.Draw(image1)
util.draw_rotated_text(image1, "Blindspot", (30,10), 0, font=fontJ, fill=(0,0,0) )
util.draw_rotated_text(image1, "Indicator", (30,20), 0, font=fontJ, fill=(0,0,0) )

disp.display(image1)

CarVideo = cv2.VideoCapture('cars.mp4')
counter = 0
while CarVideo.isOpened():
    ret, frame = CarVideo.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    controlkey = cv2.waitKey(1)
    if ret:        
        cars_frame, in_blindspot = detect.detect_cars_and_pedestrain(gray)
        cv2.imshow('frame', cars_frame)
    else:
        break
    if controlkey == ord('q'):
        break

    print("frame %d, true %d" % (counter, in_blindspot))
    counter += 1

    if (in_blindspot):
        draw.ellipse((5,10,25,30), outline=(255,0,0), fill=(255,0,0))
    else:
        draw.ellipse((5,10,25,30), outline=(255,255,255), fill=(255,255,255))

    disp.display(image1)

CarVideo.release()
cv2.destroyAllWindows()

