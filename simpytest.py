#!/usr/bin/python
# This is  simple test client for publishing data to the mqtt broker
# It parses an input file in csv format and maps the rows to a mqtt payload
# Configuration file is config.ini and must be in the same directory of the script
# It contains 2 main sections:
#  - [general]: contains general parameters needed by the script (broker address, input file, queue)
#  - [data]:    contains the mapping of the columns to the mqtt payload in the form filed = column number 
#
import time
import os, json
import uuid
import simpy
import csv
import itertools
import paho.mqtt.client as mqtt
from ConfigParser import SafeConfigParser

def on_connect(client, userdata, flags, rc):
	m="Connected flags"+str(flags)+"result code "\
	+str(rc)+"client1_id  "+str(client)
	print(m)

def on_message(client1, userdata, message):
	print("message received  "  ,str(message.payload.decode("utf-8")))

def on_log(client, userdata, level, buf):
	print("log: ",buf)


class Simulation(object):
        counter = 1
        broker_address = ""
	interval = 0.0
	dataColumns = {}
	queue = ""
	datafile = ""

	def __init__(self,env):
		self.env = env
		# Start the run process everytime an instance is created
		parser = SafeConfigParser()
                parser.read('config.ini')
		self.broker_address = parser.get('general', 'broker')
		self.interval = parser.get('general', 'interval')
		self.queue = parser.get('general', 'queue')
		for section_name in parser.sections():
			print 'Section', section_name
			print ' Options:', parser.options(section_name)
			if (section_name == 'data'):
				for name, value in parser.items(section_name):
					print ' %s = %s' %(name, value)
					self.dataColumns[name] = value
		print self.dataColumns.items()
		self.datafile = parser.get('general', 'datafile')
		self.action = env.run(self.run())

	def run(self):
		while True:
			print('Sending data to broker '+str(self.counter))
			client1 = mqtt.Client("P1")    #create new instance
			client1.on_connect= on_connect        #attach function to callback
			client1.on_message=on_message        #attach function to callback
			time.sleep(1)
 			print(self.broker_address)
			client1.connect(self.broker_address)      #connect to broker
			client1.loop_start()    #start the loop
			client1.subscribe(self.queue)
			with open(self.datafile, 'r') as f:
				row =  next(itertools.islice(csv.reader(f), self.counter, None))
				mqttData = {}
				for key in self.dataColumns:
					print key, 'corresponds to', self.dataColumns[key]
					mqttData[key] = row[int(self.dataColumns[key])-1]
				print json.dumps(mqttData)
			client1.publish("dataset/1",json.dumps(mqttData))
			client1.on_log=on_log
			time.sleep(float(self.interval))
			client1.disconnect()
			client1.loop_stop()
			self.counter+=1

env = simpy.Environment()
simulation = Simulation(env)
env.run()

