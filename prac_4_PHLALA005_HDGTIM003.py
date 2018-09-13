#!/usr/bin/python

import spidev
import time
import os
import sys
import RPi.GPIO as GPIO

# Define sensor channels
channel = 0

# Define delay between readings in sec
delay = 0.5
delay_table = [0.5, 1, 2]

# Define array which stores first 5 variables
storage = [[],[],[],[],[]]

# Define variable to track stop: 0 stop is off, 1 stop is on
stop = 0

# Define Timer Variable in sec
time = 0

# Setup GPIO for buttons
GPIO.setmode(GPIO.BCM)

# Setup pin numbers
reset_pin = 17
freq_pin = 18
stop_pin=22
display_pin=23

# Setup pins
GPIO.setup(reset_pin, GPIO.IN, pull_up_pull_down=GPIO.PUD_UP)
GPIO.setup(freq_pin, GPIO.IN, pull_up_pull_down=GPIO.PUD_UP)
GPIO.setup(stop_pin, GPIO.IN, pull_up_pull_down=GPIO.PUD_UP)
GPIO.setup(display_pin, GPIO.IN, pull_up_pull_down=GPIO.PUD_UP)

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

# Functions for buttons
def reset():
	time = 0
	storage = [[],[],[],[],[]]
	print("Time      Timer      Pot      Temp      Light")

def freq():
	id = delay_table.index(delay)
	if (id+1 >= len(delay_table):
		delay = delay_table[0]
	else:
		delay = delay_table[id+1]

# Setup GPIO interrupts
GPIO.add_event_detect(reset_pin, GPIO.FALLING, callback=reset, bouncetime=200)
GPIO.add_event_detect(freq_pin, GPIO.FALLING, callback=freq, bouncetime=200)
GPIO.add_event_detect(stop_pin, GPIO.FALLING, callback=stop, bouncetime=200)
GPIO.add_event_detect(display_pin, GPIO.FALLING, callback=display, bouncetime=200)

try:
	print("Time      Timer      Pot      Temp      Light")
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
	GPIO.cleanup()
