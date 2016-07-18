# Python module for control of Avion bluetooth dimmers
#
# Copyright 2016 Matthew Garrett <mjg59@srcf.ucam.org>
#
# This code is released under the terms of the GPLv3 license. See the
# LICENSE file for more details.

import BDAddr
from BluetoothSocket import BluetoothSocket, hci_devba
import socket
import csrmesh

def get_handles(sock):
  start = 1
  handles = {}
  while True:
    response = []
    data = bytearray([0x00])
    startlow = start & 0xff
    starthigh = (start >> 8) & 0xff
    packet = bytearray([0x08, startlow, starthigh, 0xff, 0xff, 0x03, 0x28])
    sock.send(packet)
    data = sock.recv(32)
    for d in data:
      response.append(ord(d))
    if response[0] == 1:
      return handles
    length = response[1]
    position = 2
    while position < len(data):
      handle = response[position+3] | (response[position+4] << 8)
      if length == 7:
        handle_id = response[position+5] | (response[position+6] << 8)
        handles[handle_id] = handle
      else:
        handle_uuid = ""
        for i in range(position+5, position+21):
          handle_uuid += "%02x" % response[i]
        handles[handle_uuid] = handle
      if handle > start:
        start = handle + 1
      position += length

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
    self.password = csrmesh.network_key(password)
  def connect(self):
    my_addr = hci_devba(0) # get from HCI0
    dest = BDAddr.BDAddr(self.mac)
    addr_type = BDAddr.TYPE_LE_PUBLIC
    self.sock = BluetoothSocket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
    self.sock.bind_l2(0, my_addr, cid=4, addr_type=BDAddr.TYPE_LE_RANDOM)
    self.sock.connect_l2(0, dest, cid=4, addr_type=addr_type)

    handles = get_handles(self.sock)
    self.lowhandle = handles['000b005b02000380e311af9d00c0edc4']
    self.highhandle = handles['000b005b02000480e311af9d00c0edc4']
  def set_brightness(self, brightness):
    packet = bytearray([0x80, 0x80, 0x73, 0x00, 0x0a, 0x00, 0x00, 0x00, brightness, 0x00, 0x00, 0x00, 0x00])
    csrpacket = csrmesh.make_packet(self.password, csrmesh.random_seq(), packet)
    send_packet(self.sock, self.lowhandle, csrpacket[0:20])
    send_packet(self.sock, self.highhandle, csrpacket[20:])
