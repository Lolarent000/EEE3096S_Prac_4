#!/usr/bin/python

import spidev
import time
import os
import sys

# Open SPI bus
spi = spidev.SpiDev() # create spi object
spi.open(0,0)

# RPI has one bus (#0) and two devices (#0 & #1)
# function to read ADC data from a channel
def GetData(channel): # channel must be an integer 0-7
	adc = spi.xfer2([1,(8+channel)<<4,0]) # sending 3 bytes
	data = ((adc[1]&3) << 8) + adc[2]
	return data

# function to convert data to voltage level,
# places: number of decimal places needed
def ConvertVolts(data,places):
	volts = (data * 3.3) / float(1023)
	volts = round(volts,places)
	return volts

# Define sensor channels
channel = 0

# Define delay between readings
delay = .5

try:
	while True:
		# Read the data
		sensr_data = GetData (channel)
		sensor_volt = ConvertVolts(sensor_data,2)

		# Wait before repeating loop
		time.sleep(delay)
except Exception as e:
	print(e)

finally:
	spi.close()
