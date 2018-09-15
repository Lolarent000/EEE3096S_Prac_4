#!/usr/bin/python

import spidev
import time
import os
import sys
import RPi.GPIO as GPIO
from datetime import datetime

# Define sensor channels
channel0 = 0
channel1 = 1
channel2 = 2
# Define delay between readings in sec
delay = 0.5
delay_table = [0.5, 1, 2]

# Define array which stores first 5 variables
storage = [[],[],[],[],[]]

# Define variable to track stop: 0 stop is off, 1 stop is on
stop = 0

# Define Timer Variable in sec
timer_ = 0

# Setup GPIO for buttons
GPIO.setmode(GPIO.BCM)

# Setup pin numbers
reset_pin = 17
freq_pin = 18
stop_pin=22
display_pin=23

# Setup pins
GPIO.setup(reset_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(freq_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(display_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Open SPI bus
spi = spidev.SpiDev() # Create spi object
spi.open(0,0)

# RPI has one bus (#0) and two devices (#0 & #1)
# Function to read ADC data from a channel
def GetData(channel): # Channel must be an integer 0-7
	adc = spi.xfer2([1,(8+channel)<<4,0]) # Sending 3 bytes
	data = ((adc[1]&3) << 8) + adc[2]
	return data

# Function to convert data to voltage level,
# Places: number of decimal places needed
def ConvertVolts(data,places):
	volts = (data * 3.3) / float(1023)
	volts = round(volts,places)
	return volts

# Function for formatting the time variable
def time_format(t):
	seconds = t % 60
	t -= seconds
	minutes = t % 3600
	t -= minutes
	hours = t / 3600

# Functions for buttons
def reset(channel):
	timer_ = 0
	storage = [[],[],[],[],[]]
	print("Time      Timer      Pot      Temp      Light")

def freq(channel):
	id = delay_table.index(delay)
	if (id+1 >= len(delay_table)):
		delay = delay_table[0]
	else:
		delay = delay_table[id+1]
def stop(channel):
	if(stop == 0):
		stop = 1
	else:
		stop = 0
		storage = [[],[],[],[],[]]

def display(channel):
	for item in storage:
		# Print storage item (remember it will be item [array value])
		print('{}	{}	{}V	{}	{}%'.format(item[0], item[1], item[2], item[3], item[4]))

# Setup GPIO interrupts
GPIO.add_event_detect(reset_pin, GPIO.FALLING, callback=reset, bouncetime=200)
GPIO.add_event_detect(freq_pin, GPIO.FALLING, callback=freq, bouncetime=200)
GPIO.add_event_detect(stop_pin, GPIO.FALLING, callback=stop, bouncetime=200)
GPIO.add_event_detect(display_pin, GPIO.FALLING, callback=display, bouncetime=200)

try:
	print("Time		Timer		Pot		Temp		Light")
	while True:
		if(stop == 0):
			# Read the data and print
			temp = (ConvertVolts(GetData(channel1))-0.5)/0.01
			light = (ConvertVolts(GetData(channel0))/3.3)*100
			print('{}	{}	{}V	{}	{}%'.format(datetime.now().strftime('%H:%M:%S'), time_format(timer_), ConvertVolts(GetData(channel2)), temp, round(light,2)))

		else:
			# Store data incrementally if storage isn't full
			if (storage[0] != []):
				for item in storage:
					if(item != []):
						temp = (ConvertVolts(GetData(1))-0.5)/0.01
						light = (ConvertVolts(GetData(0))/3.3)*100
						item = [datetime.now().strftime('%H:%M:%S'), time_format(timer_), ConvertVolts(GetData(2)), temp, round(light,2)]
						break

		# Wait before repeating loop
		time.sleep(delay)

except Exception as e:
	print(e)

finally:
	spi.close()
	GPIO.cleanup()
