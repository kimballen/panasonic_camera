# Panasonic WV-NW502S Camera I/O Integration for Home Assistant

A custom Home Assistant integration for controlling and monitoring I/O ports on Panasonic network cameras.

## Features

- 📊 Sensor entities for input terminals
- 🔌 Switch entities for output terminals 
- 🔄 Automatic discovery of available I/O ports
- 📡 Automatic terminal state updates via polling
- ⚙️ Configuration via UI config flow
- 📈 State attributes including raw state and terminal mode
- 🌐 Asynchronous communication using aiohttp

## Supported Models

- WV-NW502S and compatible Panasonic network cameras

## Installation

1. Copy the `panasonic_io` folder to your `custom_components` directory
2. Restart Home Assistant
3. Add integration through Home Assistant UI:
   - Go to Configuration > Integrations
   - Click "+ ADD INTEGRATION"
   - Search for "Panasonic Camera I/O"

## Requirements

- Home Assistant 2023.x or newer
- Panasonic network camera with I/O functionality
- Network connectivity to camera
- `aiohttp >= 3.8.0`

## Use Cases

This integration enables home automation scenarios using Panasonic security camera I/O terminals as sensors and actuators in your Home Assistant installation. Common applications include:

- Motion detection triggers
- Door/window sensors
- External lighting control
- Gate/access control integration


