
# Python module for control of Avion bluetooth dimmers
#
# Copyright 2016 Matthew Garrett <mjg59@srcf.ucam.org>
#
# This code is released under the terms of the GPLv3 license. See the
# LICENSE file for more details.

import csrmesh
import requests
from bluepy import btle


def get_devices(username: str, password: str, connect: bool = False):
    """Enumerate devices using the Avi-on API."""
    API_URL = "https://api.avi-on.com/{api}"
    API_AUTH = API_URL.format(api='sessions')
    API_USER = API_URL.format(api='user')
    API_DEVICES = API_URL.format(api='locations/{location}/abstract_devices')

    def _authenticate(username, password):
        """Authenticate with the API and get a token."""
        auth_data = {'email': username, 'password': password}
        r = requests.post(API_AUTH, json=auth_data)
        try:
            return r.json()['credentials']['auth_token']
        except KeyError:
            raise(AvionException('API authentication failed'))

    def _get_locations(auth_token):
        """Get a list of locations from the API."""
        headers = {'Authorization': 'Token {}'.format(auth_token)}
        r = requests.get(API_USER, headers=headers)
        return r.json()['user']['locations']

    def _get_devices(auth_token, location_id):
        """Get a list of devices for a particular location."""
        headers = {'Authorization': 'Token {}'.format(auth_token)}
        r = requests.get(API_DEVICES.format(location=location_id),
                         headers=headers)
        return r.json()['abstract_devices']

    auth_token = _authenticate(username, password)
    locations = _get_locations(auth_token)
    all_devices = []
    for location_idx, location in enumerate(locations):
        devices = _get_devices(auth_token, location['id'])
        locations[location_idx]['devices'] = []
        for device_id, device in enumerate(devices):
            all_devices.append(Avion(
                mac=''.join(l + ':' * (n % 2)
                            for n, l in
                            enumerate(device['friendly_mac_address']))[:17],
                passphrase=location['passphrase'],
                name=device['name'],
                object_id=len(devices) - device_id,
                connect=connect))

    return all_devices


class AvionException(Exception):
    """An error related to an Avi-on bluetooth device."""

    pass


class Avion:
    """An Avi-on bluetooth device."""

    CHARACTERISTIC_LOW = btle.UUID("c4edc000-9daf-11e3-8003-00025b000b00")
    CHARACTERISTIC_HIGH = btle.UUID("c4edc000-9daf-11e3-8004-00025b000b00")
    KEY_SUFFIX = bytearray([0x00, 0x4d, 0x43, 0x50])
    BRIGHTNESS_PREFIX = bytearray([0x73, 0x00, 0x0a, 0x00, 0x00, 0x00])
    BRIGHTNESS_SUFFIX = bytearray([0x00, 0x00, 0x00, 0x00])
    DEFAULT_OBJECT = bytearray([0x00, 0x00])
    DEFAULT_NAME = "Avi-On Switch"

    def __init__(self, mac: str, passphrase: str, name: str = None,
                 object_id: int = None, connect: bool = True):
        """Configure and optionally connect to this device.

        If using more than one Avi-on device, object_id is required to
        distinguish devices. Otherwise all devices will switch together."""
        self.name = name or self.DEFAULT_NAME
        self.mac = mac
        self.key = csrmesh.crypto.generate_key(
            passphrase.encode("ascii") + self.KEY_SUFFIX)
        self.object_id = object_id
        self.device = None
        if connect:
            self.connect()

    def __repr__(self):
        """Representation of this object."""
        return '<Avion name={name}, mac={mac}, id={object_id}>'.format(
            name=self.name, mac=self.mac, object_id=self.object_id)

    def connect(self):
        """Connect to this device."""
        try:
            self.device = btle.Peripheral(self.mac,
                                          addrType=btle.ADDR_TYPE_PUBLIC)
        except btle.BTLEException:
            raise AvionException("Failed to connect to device {mac}"
                                 .format(mac=self.mac))
        self._get_characteristic_handles()

    def _get_characteristic_handles(self):
        """Get high/low characteristic handles.

        Communicates with the device to get the handles for the "high" and
        "low" characteristics. These will later be used for sending commands.
        """
        try:
            characteristics = self.device.getCharacteristics()
            for characteristic in characteristics:
                if characteristic.uuid == self.CHARACTERISTIC_LOW:
                    self.handle_low = characteristic.getHandle()
                elif characteristic.uuid == self.CHARACTERISTIC_HIGH:
                    self.handle_high = characteristic.getHandle()
        except btle.BTLEException:
            raise AvionException("Failed to read characteristics for device "
                                 "{mac}".format(mac=self.mac))

    def set_brightness(self, brightness):
        """Update the brightness of this device."""
        if self.object_id:
            object_bytes = bytearray([0x7f + self.object_id, 0x80])
        else:
            object_bytes = self.DEFAULT_OBJECT
        packet = (object_bytes +
                  self.BRIGHTNESS_PREFIX +
                  bytearray([brightness]) +
                  self.BRIGHTNESS_SUFFIX)
        csrpacket = csrmesh.crypto.make_packet(
            self.key, csrmesh.crypto.random_seq(), packet)
        try:
            self.device.writeCharacteristic(
                self.handle_low, csrpacket[0:20], withResponse=True)
            self.device.writeCharacteristic(
                self.handle_high, csrpacket[20:], withResponse=True)
        except Exception:
            raise AvionException("Unable to send brightness command")

    def turn_on(self):
        """Turn the device on."""
        self.set_brightness(255)

    def turn_off(self):
        """Turn the device off."""
        self.set_brightness(0)
