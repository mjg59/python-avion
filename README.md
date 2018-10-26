# Python control for Avi-on bluetooth dimmers and switches

A simple Python API for controlling [Avi-on](http://www.avi-on.com/) Bluetooth dimmers and switches. This code makes use of the PyBT2 branch of Mike Ryan's [PyBT](http://github.com/mikeryan/PyBT) and depends on [csrmesh](https://github.com/nkaminski/csrmesh/).


## Usage: With the Avion API (easy)

This is the easy way to use the library. It uses the Avi-On API to get the devices in your account.

```python
import avion

username = 'your-avion-username@example.com'
password = 'your-avion-password'

# Get all Avi-On devices in your account:
devices = avion.get_devices(username, password)
for device in avion.get_devices():
    device.turn_on()
    device.set_brightness(128)
    device.turn_off()
```

By default, a connection won't be attempted until the first command is sent. To connect immediately, use `get_devices(username, password, connect=True)`.


## Usage: Manual

This is an alternative approach which does not require the Avi-On API.

Get API key and password:

```
curl -X POST -H "Content-Type: application/json" -d '{"email": "fakename@example.com", "password": "password"}' https://admin.avi-on.com/api/sessions | jq
```

Replace the email and password fields with your Avion credentials. The "passphrase" field is the API key.

Replace the MAC address and API key:

```python
import avion

dimmer = avion.Avion("00:21:4d:00:00:01", "O5bb9/ab8NvaDMnKYjpTGQ==")
dimmer.connect()
dimmer.set_brightness(255)
```

Note: Despite specifying a MAC address, the code above will set brightness on
every Avi-on dimmer on the local mesh network. To control just one device,
you must specify its object ID (integer starting from 1).

```python
import avion

dimmer = avion.Avion("00:21:4d:00:00:01", "O5bb9/ab8NvaDMnKYjpTGQ==")
dimmer.connect()

# Set device 1 to 50% brightness.
dimmer.set_brightness(0x80, 1)

# Set device 2 to 100% brightness.
dimmer.set_brightness(0xff, 2)
```
