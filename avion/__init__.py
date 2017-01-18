# Python module for control of Avion bluetooth dimmers
#
# Copyright 2016 Matthew Garrett <mjg59@srcf.ucam.org>
#
# This code is released under the terms of the GPLv3 license. See the
# LICENSE file for more details.

import csrmesh
import socket
import time

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

class avion:
  def __init__(self, mac, password):
    self.mac = mac
    password = password.encode("ascii") + bytearray([0x00, 0x4d, 0x43, 0x50])
    self.password = csrmesh.network_key(password)
  def connect(self):
    self.device = btle.Peripheral(self.mac, addrType=btle.ADDR_TYPE_PUBLIC)
    characteristics = self.device.getCharacteristics()
    for characteristic in characteristics:
      if characteristic.uuid == "c4edc000-9daf-11e3-8003-00025b000b00":
        self.lowhandle = characteristic.getHandle()
      elif characteristic.uuid == "c4edc000-9daf-11e3-8004-00025b000b00":
        self.highhandle = characteristic.getHandle()
  def set_brightness(self, brightness):
    packet = bytearray([0x80, 0x80, 0x73, 0x00, 0x0a, 0x00, 0x00, 0x00, brightness, 0x00, 0x00, 0x00, 0x00])
    csrpacket = csrmesh.make_packet(self.password, csrmesh.random_seq(), packet)
    initial = time.time()
    while True:
      if time.time() - initial >= 10:
        return False
      try:
        self.device.writeCharacteristic(self.lowhandle, csrpacket[0:20], withResponse=True)
        self.device.writeCharacteristic(self.highhandle, csrpacket[20:], withResponse=True)
      except Exception as e:
        try:
          self.connect()
        except:
          pass
    return True
