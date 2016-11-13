#!/usr/bin/env python

import time
import numpy

import Adafruit_ADS1x15

from subprocess import call
from time import gmtime, strftime


# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1
DR = 64
READINGS_PER_SECOND = numpy.int32(120)
DELAY = numpy.float32(1.0/120) - numpy.float32(0.205/120)
NOISE_AVG = numpy.float32(3.56)
RATIO_TO_W = numpy.float32(1/3.33)

API_KEY="ef45e7b1a19b527130339fe7c984f7a0"
URL="http://10.0.0.253:9004/input/post.json"



FD = open("reading.log", 'w')


# Once continuous ADC conversions are started you can call get_last_result() to
# retrieve the latest result, or stop_adc() to stop conversions.

def get_avg_second():
	buff_second = numpy.array(numpy.zeros(READINGS_PER_SECOND+20, dtype=numpy.int32))
	l_time = time.time() + 1
	b = 0
	while(time.time() < l_time):
		buff_second[b] = adc.get_last_result()
		b += 1
		time.sleep(DELAY)
	val = (numpy.float32(numpy.sum(buff_second)/numpy.float32(b))-NOISE_AVG)*RATIO_TO_W
	#FD.write(" "+str(val/1000.0)+" kW\n")
	print str(val/1000.0)+ " kW"
	return val

def get_avg_hour():
	buff_hour = numpy.array(numpy.zeros(3600, dtype=numpy.float64))
	l_time = time.time() + 3600
	for i in range(3600):
		if (i%60 == 0):
			print "## Minute "+str(i/60)
			FD.write("## Minute "+str(i/60)+"\n")
			FD.flush()
		buff_hour[i] = numpy.float64(get_avg_second()) # using 64bit floats
	v = numpy.mean(buff_hour)	# result in kWH
	return v

def get_avg_day():
	buff_day = numpy.array(numpy.zeros(24, dtype=numpy.float64))
	for i in range(24):
		print "### Hour "+str(i)
		FD.write("### Hour "+str(i))
		buff_day[i] = get_avg_hour()
		print "# Spent "+ str(buff_day[i]) + " kWH"
		FD.write("# Spent "+ str(buff_day[i]) + " kWH\n")
		print buff_day
		print "#######################################"
	print "Total Spent: "+str(numpy.sum(buff_day)/1000.0)+ "kWH"
	FD.write("################################\n")
	FD.write("# Total Spent "+ str(numpy.sum(buff_day)/1000.0) + " kWH\n")
	FD.flush()
	FD.close()


#logging.basicConfig(filename='readings.log',level=logging.DEBUG)

# Start continuous ADC conversions on channel 0 using the previously set gain
# value.  Note you can also pass an optional data_rate parameter, see the simpletest.py
# example and read_adc function for more infromation.
adc.start_adc(0, gain=GAIN, data_rate=DR)

#logging.debug("Stabilize Readings")
#give some time to stabilize
adc.get_last_result()
time.sleep(0.05)

print("Int Continuous sampling")

while True:
	buff = numpy.array(numpy.zeros(5, dtype=numpy.float32))
	for i in range(5):
		buff[i] = get_avg_second()

	call(["curl", "--data", "data={Consumption power:"+str(numpy.mean(buff))+"}", URL+"?node=ClamPi&apikey="+API_KEY])
	#call(["curl", "--data", "data={$(cat /proc/net/wireless|grep wlan0|awk '{print \'Wifi Link Quality:"$3"0,","Wifi Signal Level:"$4 0}')}"", URL+"?node=ClamPi&apikey="+API_KEY])

	#http://10.0.0.253:9004/device/set.json?id=0
	#print("Sent")

#print("Starting ", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
#get_avg_day()


#print("Ended ", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

adc.stop_adc()
