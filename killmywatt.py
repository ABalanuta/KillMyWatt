#!/usr/bin/env python

import os
import sys
import signal
import threading
import subprocess
import time
import numpy
import requests

import Adafruit_ADS1x15
from collections import deque



GAIN = 1
DR = 860
READINGS_PER_SECOND = numpy.int32(DR)
NOISE_AVG = numpy.float32(3.56)
RATIO_TO_W = numpy.float32(1/3.33)

API_KEY="ef45e7b1a19b527130339fe7c984f7a0"
URL="http://10.0.0.253:9004/input/post.json"


def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')
	try:
		if cthread.stop:
			cthread.stop()
		if adc.stop_adc:
			adc.stop_adc()
	except:
		print 'Error Stoping Curl Thread !'
		pass
	sys.exit(0)

class CurlThread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.running = True

	def run(self):
		while self.running:
			if len(q) > 0:
				sum = 0
				while len(q) > 0:
					sum = sum + q.pop()
				url = URL+"?json={Consumption power:"+str(sum)+"}&node=ClamPi&apikey="+API_KEY
				try:
					r = requests.get(url, allow_redirects=True)
					print("Send ok", sum, "W")
				except:
					# if failed, send later
					print("Error Sending")
					q.append(sum)
					time.sleep(2.5)
					pass
			else:
				time.sleep(0.5)

	def stop(self):
		self.running = False

# Once continuous ADC conversions are started you can call get_last_result() to
# retrieve the latest result, or stop_adc() to stop conversions.
def get_avg_five_second():
	b = 0
	l_time = time.time() + 5
	while(time.time() < l_time):
		buff_seconds[b] = adc.get_last_result()
		b += 1
	val = ( numpy.float32( numpy.sum(buff_seconds[0:b]) / numpy.float32(b) ) - NOISE_AVG) * RATIO_TO_W
	print str(val/1000.0)+ " kW"
	return val

#
signal.signal(signal.SIGINT, signal_handler)

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

#Buffer where the values will be stored
buff_seconds = numpy.array(numpy.zeros(READINGS_PER_SECOND*5, dtype=numpy.int32))

# A queue for interthread communication
q = deque()


# Start continuous ADC conversions on channel 0 using the previously set gain
# value.  Note you can also pass an optional data_rate parameter, see the simpletest.py
# example and read_adc function for more infromation.
adc.start_adc(0, gain=GAIN, data_rate=DR)

#logging.debug("Stabilize Readings")
#give some time to stabilize
adc.get_last_result()
time.sleep(0.05)

# Create and start the curl thread
cthread = CurlThread()
cthread.start()

print("Int Continuous sampling")

while True:
	q.append(get_avg_five_second())
