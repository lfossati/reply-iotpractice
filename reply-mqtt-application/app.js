/*eslint-env node*/

//------------------------------------------------------------------------------
// node.js application for the IoT practice development project
// The application exposes functionality for switching on and off a light attached a RaspberryPi connected to the Bluemix platform
// through the IBM IoTF Foundation service
// It is intended to be deployed in the Node.js Bluemix runtime using CloudFoundry
//------------------------------------------------------------------------------

// This application uses express as its web server
var express = require('express');

// cfenv provides access to your Cloud Foundry environment
// for more info, see: https://www.npmjs.com/package/cfenv
var cfenv = require('cfenv');

var handleTimeout = function (req, res, next) {
    if (!req.timedout) next();
};


// create a new express server
var app = express();

var bodyParser = require('body-parser');

// serve the files out of ./public as our main files
app.use(express.static(__dirname + '/public'));

// get the app environment from Cloud Foundry
var appEnv = cfenv.getAppEnv();


var deviceType = "RaspberryPi";

// iotPlatform server name
var iotPlatformServiceName = 'reply-mqtt-broker-iotf-service';

//IBM IoT service
var Client = require('ibmiotf').IotfApplication;

// this iot service credentials 
var iotCredentials;

//Loop through configuration internally defined in Bluemix and retrieve the credential from the IoT service
var baseConfig = appEnv.getServices(iotPlatformServiceName);
iotCredentials = baseConfig[iotPlatformServiceName];

console.log('iot config is ' + JSON.stringify(iotCredentials));

var iotAppConfig = {
 "org" : iotCredentials.credentials.org,
 "id" : iotCredentials.credentials.iotCredentialsIdentifier,
 "auth-method" : "apikey",
 "auth-key" : iotCredentials.credentials.apiKey,
 "auth-token" : iotCredentials.credentials.apiToken
} 


var appClient = new Client(iotAppConfig);

appClient.connect();
console.log("Successfully connected to our IoT service!");

// subscribe to input events 
appClient.on("connect", function () {
 console.log("subscribe to input events");
 appClient.subscribeToDeviceEvents("RaspberryPi");
});


var sensorData = {"lightStatus":{}};

// deviceType "raspberrypi" and eventType "data" are published by client.py on RaspberryPi
appClient.on("deviceEvent", function(deviceType, deviceId, eventType, format, payload){
	if (eventType === 'data'){
		sensorData.lightStatus = JSON.parse(payload);
		sensorData.deviceId = deviceId
	}
});


// Set the route for getting the status of the device (GET /device/deviceid)
// The URI will return the status of the light (off/on, 0/1) of device deviceid
app.get('/device/:deviceId', function(req, res) {
	 var deviceId = req.params.deviceId;
	 if (sensorData.deviceId == deviceId) {
		 console.log("status to device type "+deviceType+" with device id "+deviceId);
		 return res.send(sensorData.lightStatus); 
	 }
});

// Set the route for switching on the device (GET /lighton/deviceid)
// By requesting this URI it will be possible to switch the light on of the device deviceid
app.get('/lighton/:deviceId', function(req, res) {
	 var deviceId = req.params.deviceId;
	 console.log("Trying to publish status to device type "+deviceType+" with device id "+deviceId);
	 myData={'switch':'on'};
	 appClient.publishDeviceEvent(deviceType, deviceId, "light", "json", myData);
	 return res.send({"status":"OK"});
});

// Set the route for switching on the device (GET /lightoff/deviceid)
// By requesting this URI it will be possible to switch the light on of the device deviceid
app.get('/lightoff/:deviceId', function(req, res) {
	 var deviceId = req.params.deviceId;
	 console.log("Trying to publish status to device type "+deviceType+" with device id "+deviceId);
	 myData={'switch':'off'};
	 appClient.publishDeviceEvent(deviceType, deviceId, "light", "json", myData);
	 return res.send({"status":"OK"});
});

// Start nodejs server.js
app.listen(appEnv.port, '0.0.0.0', function() {
  // print a message when the server starts listening
  console.log("server starting on " + appEnv.url);
});

