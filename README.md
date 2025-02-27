Panasonic Camera I/O Integration for Home Assistant
A custom Home Assistant integration for controlling and monitoring I/O ports on Panasonic network cameras. This integration supports:

Monitoring input/output terminal states
Reading sensor data from camera I/O ports
Controlling output terminals
Configuration via UI config flow
Automatic terminal state updates via polling
Supported Models
WV-NW502S and compatible Panasonic network cameras
Features
Sensor entities for input terminals
Switch entities for output terminals
Automatic discovery of available I/O ports
State attributes including raw state and terminal mode
Asynchronous communication using aiohttp
Requirements
Home Assistant 2023.x or newer
Panasonic network camera with I/O functionality
Network connectivity to camera
aiohttp >= 3.8.0
This integration enables home automation scenarios using Panasonic security camera I/O terminals as sensors and actuators in your Home Assistant installation.
