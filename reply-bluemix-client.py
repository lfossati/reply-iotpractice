#!/usr/bin/python
# This is only executed on the device client e.g. Raspberry Pi
# This client connects the device to the IBM IoTF bluemix service 
# and it regularly publishes status data (if light is on  or off)
# Wait for events published by the app for switching the light on or off
import time
import os, json
import ibmiotf.application
import uuid
import RPi.GPIO as GPIO

client = None

lightGPIOPort1 = 18
lightGPIOPort2 = 23

configFile = "/home/pi/iotpythonclient/device.cfg"

# This function is invoked when a new event is published for the device
def myCommandCallback(cmd):
        print "Command received: %s event %s" % (cmd.data, cmd.event )
        # In case the event is of type light and with payload {switch : on} or {switch : off} turn the light on/off
		if cmd.event == "light":
                                for k in cmd.data:
                                                        if (k == "switch"):
                                                                        if (cmd.data[k] == "on"):
                                                                                                print "Got command for switching the light on"
                                                                                                GPIO.output(lightGPIOPort1, True)
                                                                                                GPIO.output(lightGPIOPort2, True)
                                                                        if (cmd.data[k] == "off"):
                                                                                                print "Got command for switching the light off"
                                                                                                GPIO.output(lightGPIOPort1, False)
                                                                                                GPIO.output(lightGPIOPort2, False)

if __name__ == "__main__":
        # Set the RaspberryPi output ports through GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(lightGPIOPort1, GPIO.OUT)
        GPIO.setup(lightGPIOPort2, GPIO.OUT)
        try:
		        # Connects the device to the IoTf service
                options = ibmiotf.application.ParseConfigFile(configFile)
                options["deviceId"] = options["id"]
                options["id"] = "aaa" + options["id"]
                client = ibmiotf.application.Client(options)
                print "try to connect to IoT"
                client.connect()
                print "connect to IoT successfully"
				# Register the device callback and subscribe the client to the light event
                client.deviceEventCallback = myCommandCallback
                client.subscribeToDeviceEvents(event="light")

                # Loops for reading the status of the light and communicating it to Bluemix
				while True:
                        statusData = {}
                        statusData['status'] = GPIO.input(18)
                        jsonLightStatusData = json.dumps(statusData)
                        print jsonLightStatusData
                        client.publishEvent("RaspberryPi", options["deviceId"], "data", "json", jsonLightStatusData)
                        time.sleep(1)
        except ibmiotf.ConnectionException as e:
                print e
