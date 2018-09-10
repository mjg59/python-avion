# Python module for control of Avion bluetooth dimmers
#
# Copyright 2016 Matthew Garrett <mjg59@srcf.ucam.org>
#
# This code is released under the terms of the GPLv3 license. See the
# LICENSE file for more details.

import csrmesh
import requests
import socket

from bluepy import btle

def send_packet(sock, handle, data):
  packet = bytearray([0x12, handle, 0x00])
  for item in data:
    packet.append(item)
  sock.send(packet)
  data = sock.recv(32)
  response = []
  for d in data:
    response.append(ord(d))
  return response

def read_packet(sock, handle):
  packet = bytearray([0x0a, handle, 0x00])
  sock.send(packet)
  data = sock.recv(32)
  response = []
  for d in data:
    response.append(ord(d))
  return response

def avion_info(username, password):
  """Enumerate devices using the Avi-On API."""
  def _authenticate(username, password):
    """Authenticate with the API and get a token."""
    r = requests.post("https://api.avi-on.com/sessions",
                      json={'email': username, 'password': password})
    try:
      return r.json()['credentials']['auth_token']
    except KeyError:
      raise(avionException('API authentication failed'))

  def _get_locations(auth_token):
    """Get a list of locations from the API."""
    r = requests.get("https://api.avi-on.com/user",
                     headers={'Authorization': 'Token {}'.format(auth_token)})
    return r.json()['user']['locations']

  def _get_devices(auth_token, location_id):
    """Get a list of devices for a particular location."""
    r = requests.get("https://api.avi-on.com/locations/{}/abstract_devices"
                       .format(location_id),
                     headers={'Authorization': 'Token {}'.format(auth_token)})
    return r.json()['abstract_devices']

  auth_token = _authenticate(username, password)
  locations = _get_locations(auth_token)
  for idx, location in enumerate(locations):
    devices = _get_devices(auth_token, location['id'])
    locations[idx]['devices'] = [{'device': d} for d in devices]
  return {'locations': [{'location': l} for l in locations]}


class avionException(Exception):
  pass

class avion:
  def __init__(self, mac, password):
    self.mac = mac
    password = password.encode("ascii") + bytearray([0x00, 0x4d, 0x43, 0x50])
    self.password = csrmesh.crypto.generate_key(password)

  def connect(self):
    try:
      self.device = btle.Peripheral(self.mac, addrType=btle.ADDR_TYPE_PUBLIC)
      characteristics = self.device.getCharacteristics()
      for characteristic in characteristics:
        if characteristic.uuid == "c4edc000-9daf-11e3-8003-00025b000b00":
          self.lowhandle = characteristic.getHandle()
        elif characteristic.uuid == "c4edc000-9daf-11e3-8004-00025b000b00":
          self.highhandle = characteristic.getHandle()
    except btle.BTLEException:
      raise avionException("Unable to connect")

  def set_brightness(self, brightness, object_id = 0):
    obj_a = obj_b = 0x00
    if object_id:
      obj_a = 0x7f + object_id
      obj_b = 0x80
    packet = bytearray([obj_a, obj_b, 0x73, 0x00, 0x0a, 0x00, 0x00, 0x00, brightness, 0x00, 0x00, 0x00, 0x00])
    csrpacket = csrmesh.crypto.make_packet(self.password, csrmesh.crypto.random_seq(), packet)
    try:
      self.device.writeCharacteristic(self.lowhandle, csrpacket[0:20], withResponse=True)
      self.device.writeCharacteristic(self.highhandle, csrpacket[20:], withResponse=True)
    except Exception as e:
      raise avionException("Unable to send brightness command")
