#!/usr/bin/python

# 
# LICENSE
# 
# Copyright (c) 2010, University College Dublin, National University of
# Ireland, Dublin
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# - Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# - Neither the name University College Dublin, National University of
# Ireland, Dublin nor the names of its contributors may be used to
# endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 

from bluetooth import *
import sys

debug = True

#
# Special Exception
#
class LengthPacketException(Exception):
    def __init__(self, packet_id, value, expecting_len):
        self.value = value
        self.packet_id = packet_id
        self.spec_len = expecting_len
    def __str__(self):
        return "Packet ID 0x%02x length (%d) doesn't match to the expecting length (%d)" % (self.packet_id, ord(self.value), self.spec_len)

    # End of the class LengthPacketException


#
# Zeemote listening class
#
class ZeemoteControl():
    # Handshakes types
    HANDSHAKE_SUCCESSFUL              = "\x00"
    HANDSHAKE_NOT_READY               = "\x01"
    HANDSHAKE_ERR_INVALID_REPORT_ID   = "\x02"
    HANDSHAKE_ERR_UNSUPPORTED_REQUEST = "\x03"
    HANDSHAKE_ERR_INVALID_PARAMETER   = "\x04"
    HANDSHAKE_ERR_UNKNOWN             = "\x0E"
    HANDSHAKE_ERR_FATAL               = "\x0F"

    def __init__(self, tries_nb=3):
        self.number_of_tries = tries_nb

        self.connected = False
        self.debug_file = None
        if debug:
            try:
                self.debug_file = open("/tmp/zeemote_talking", "w")
            except IOError, (e):
                print "No debug file for this session: ", e

    def connect(self):
        address = None
        port    = None
        name    = None
        uuid = "8E1F0CF7-508F-4875-B62C-FBB67FD34812"
        service_matches = ""
        self.sock = BluetoothSocket( RFCOMM )
        try:
            if debug:
                print "Trying to find a Zeemote device..."
            while(self.number_of_tries > 0 and len(service_matches) == 0):
                self.number_of_tries -= 1
                service_matches = find_service( uuid = uuid )

            if len(service_matches) == 0:
                print "Couldn't find any Zeemote device"
                raise Exception("No zeemote device found")

            first_match = service_matches[0]
            port    = first_match["port"]
            address = first_match["host"]
            name    = first_match["name"]

            if debug:
                print "One Zeemote device found: %s (%s)" % (name, address)

            self.sock.connect((address, port))
        except KeyboardInterrupt, BluetoothError:
            print "Unable to connect to the Zeemote controller"
        else:
            # if connection succeeded
            print "Connected to %s (%s, %d)" % (name, address, port)
            self.connected = True
    
    def disconnect(self):
        if self.connected:
            self.sock.close()
            self.connected = False
            if self.debug_file:
                try:
                    self.debug_file.close()
                except:
                    pass
            print "Disconnected from the Zeemote controller"

    def listen(self):
        try:
            length = self.sock.recv(1)
            input_id = self.sock.recv(1)
        except KeyboardInterrupt:
            self.disconnect()
            return None
        except BluetoothError:
            if self.number_of_tries > 0:
                self.number_of_tries -= 1
                self.disconnect()
                if debug:
                    print "Reconnecting..."
                self.connect()
                return None
            else:
                return None

        if self.debug_file:
            self.debug_file.write(length)
            self.debug_file.write(input_id)
            self.debug_file.flush()

        if debug:
            print "Message length: %d" % ord(length)


        #
        # Here are the functions that are taking care of different IDs
        #
        def process_report_03(): # Input report #0x03
            if debug:
                print "process_report_03"
            if length != "\x2d":
                raise LengthPacketException(3, length, 45)

            data['Firmware Major Version'] = self.sock.recv(2)
            data['Firmware Minor Version'] = self.sock.recv(2)
            data['Firmware Revision'] = self.sock.recv(2)
            data['Platform ID'] = self.sock.recv(2)
            data['Model ID'] = self.sock.recv(2)
            data['Model Name Length'] = self.sock.recv(1)
            data['Model Name'] = self.sock.recv(32)

            if self.debug_file:
                self.debug_file.write(data['Firmware Major Version'])
                self.debug_file.write(data['Firmware Minor Version'])
                self.debug_file.write(data['Firmware Revision'])
                self.debug_file.write(data['Platform ID'])
                self.debug_file.write(data['Model ID'])
                self.debug_file.write(data['Model Name Length'])
                self.debug_file.write(data['Model Name'])
                self.debug_file.flush()

        def process_report_04(): # Input report #0x04
            if debug:
                print "process_report_04"
    
            if length != "\x25":
                raise LengthPacketException(4, length, 37)

            data['Button ID'] = self.sock.recv(1)
            data['Recommended Game Action'] = self.sock.recv(1)
            data['Button Description Length'] = self.sock.recv(1)
            data['Button Description'] = self.sock.recv(32)
    
            if self.debug_file:
                self.debug_file.write(data['Button ID'])
                self.debug_file.write(data['Recommended Game Action'])
                self.debug_file.write(data['Button Description Length'])
                self.debug_file.write(data['Button Description'])
                self.debug_file.flush()
    
        def process_report_05(): # Input report #0x05
            if debug:
                print "process_report_05"
    
            if length != "\x07":
                raise LengthPacketException(5, length, 7)

            data['Type'] = self.sock.recv(1)
            data['Value'] = self.sock.recv(4)
    
            if self.debug_file:
                self.debug_file.write(data['Type'])
                self.debug_file.write(data['Value'])
                self.debug_file.flush()
    
        # report #0x06 is an output report

        def process_report_07(): # Input report #0x07
            if debug:
                print "process_report_07"

            if length != "\x08":
                raise LengthPacketException(7, length, 8)

            data['Key Code 1'] = self.sock.recv(1)
            data['Key Code 2'] = self.sock.recv(1)
            data['Key Code 3'] = self.sock.recv(1)
            data['Key Code 4'] = self.sock.recv(1)
            data['Key Code 5'] = self.sock.recv(1)
            data['Key Code 6'] = self.sock.recv(1)
    
            if self.debug_file:
                self.debug_file.write(data['Key Code 1'])
                self.debug_file.write(data['Key Code 2'])
                self.debug_file.write(data['Key Code 3'])
                self.debug_file.write(data['Key Code 4'])
                self.debug_file.write(data['Key Code 5'])
                self.debug_file.write(data['Key Code 6'])
                self.debug_file.flush()

        def process_report_08(): # Input report #0x08
            if debug:
                print "process_report_08"
    
            if length != "\x05":
                raise LengthPacketException(8, length, 5)

            byte = self.sock.recv(1)
            # We keep only the extrem left bit (is only 0 or 1)
            data['Raw'] = (ord(byte) & 0x80) >> 7
            # We keep all the others bits (is an entire byte)
            data['Joystick ID'] = ord(byte) & 0x7F
            data['X-Axis Reading'] = self.sock.recv(1)
            data['Y-Axis Reading'] = self.sock.recv(1)
    
            if self.debug_file:
                self.debug_file.write(byte)
                self.debug_file.write(data['X-Axis Reading'])
                self.debug_file.write(data['Y-Axis Reading'])
                self.debug_file.flush()

        def process_report_09(): # Input report #0x09
            if debug:
                print "process_report_09"
    
            if length != "\x07":
                raise LengthPacketException(9, length, 7)

            byte = self.sock.recv(1)
            # We keep only the left bit (is only 0 or 1)
            data['Raw'] = (ord(byte) & 0x80) >> 7
            # We keep all the others bits (is an entire byte)
            data['Joystick ID'] = ord(byte) & 0x7F
            data['X-Axis Reading'] = self.sock.recv(2)
            data['Y-Axis Reading'] = self.sock.recv(2)
    
            if self.debug_file:
                self.debug_file.write(byte)
                self.debug_file.write(data['X-Axis Reading'])
                self.debug_file.write(data['Y-Axis Reading'])
                self.debug_file.flush()

        def process_report_0A(): # Input report #0x0A
            if debug:
                print "process_report_0A"
    
            if length != "\x0b":
                raise LengthPacketException(int("0x0a", 16), length, 11)

            byte = self.sock.recv(1)
            # We keep only the left bit (is only 0 or 1)
            data['Raw'] = (ord(byte) & 0x80) >> 7
            # We keep all the others bits (is an entire byte)
            data['Joystick ID'] = ord(byte) & 0x7F
            data['X-Axis Reading'] = self.sock.recv(4)
            data['Y-Axis Reading'] = self.sock.recv(4)
    
            if self.debug_file:
                self.debug_file.write(byte)
                self.debug_file.write(data['X-Axis Reading'])
                self.debug_file.write(data['Y-Axis Reading'])
                self.debug_file.flush()

        def process_report_0B(): # Input report #0x0B
            if debug:
                print "process_report_0B"
    
            if length != "\x06":
                raise LengthPacketException(int("0x0b", 16), length, 6)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_0C(): # Input report #0x0C
            if debug:
                print "process_report_0C"
    
            if length != "\x09":
                raise LengthPacketException(int("0x0c", 16), length, 9)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_0D(): # Input report #0x0D
            if debug:
                print "process_report_0D"
    
            if length != "\x0f":
                raise LengthPacketException(int("0x0d", 16), length, 15)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_0E(): # Input report #0x0E
            if debug:
                print "process_report_0E"
    
            if length != "\x04":
                raise LengthPacketException(int("0x0e", 16), length, 4)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_0F(): # Input report #0x0F
            if debug:
                print "process_report_0F"
    
            if length != "\x05":
                raise LengthPacketException(int("0x0f", 16), length, 5)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_10(): # Input report #0x10
            if debug:
                print "process_report_10"
    
            if length != "\x07":
                raise LengthPacketException(int("0x10", 16), length, 7)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_11(): # Input report #0x11
            if debug:
                print "process_report_11"

            if length != "\x04":
                raise LengthPacketException(int("0x11", 16), length, 4)

            byte1 = self.sock.recv(1)
            byte2 = self.sock.recv(1)
            data['Present Battery Voltage'] = (ord(byte1) << 8) | ord(byte2)

            if debug:
                self.debug_file.write(byte1)
                self.debug_file.write(byte2)
                self.debug_file.flush()


        def process_report_12(): # Input report #0x12
            if debug:
                print "process_report_12"
    
            if length != "\x05":
                raise LengthPacketException(int("0x12", 16), length, 5)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_13(): # Input report #0x13
            if debug:
                print "process_report_13"
    
            if length != "\x07":
                raise LengthPacketException(int("0x13", 16), length, 7)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_14(): # Input report #0x14
            if debug:
                print "process_report_14"
    
            if length != "\x0b":
                raise LengthPacketException(int("0x14", 16), length, 11)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_15(): # Input report #0x15
            if debug:
                print "process_report_15"
    
            if length != "\x04":
                raise LengthPacketException(int("0x15", 16), length, 4)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_16(): # Input report #0x16
            if debug:
                print "process_report_16"
    
            if length != "\x05":
                raise LengthPacketException(int("0x16", 16), length, 5)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        def process_report_17(): # Input report #0x17
            if debug:
                print "process_report_17"
    
            if length != "\x07":
                raise LengthPacketException(int("0x17", 16), length, 7)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        # report #0x18 and 0x19 are outputs reports

        def process_report_1A(): # Input report #0x1A
            if debug:
                print "process_report_1A"
            # Nothing to do

        def process_report_1B(): # Input report #0x1B
            if debug:
                print "process_report_1B"

            if length != "\x08":
                raise LengthPacketException(int("0x17", 16), length, 8)


            data['Protocol Major Version'] = self.sock.recv(2)
            data['Protocol Minor Version'] = self.sock.recv(2)
            data['Protocol Revision'] = self.sock.recv(2)
    
            if self.debug_file:
                self.debug_file.write(data['Protocol Major Version'])
                self.debug_file.write(data['Protocol Minor Version'])
                self.debug_file.write(data['Protocol Revision'])
                self.debug_file.flush()

        # Below are two functions for test purpose only
        def process_report_FD(): # Input report #0xFD
            if debug:
                print "process_report_FD"
    
            if length != "\x07":
                raise LengthPacketException(int("0xfd", 16), length, 7)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        # report #FE is an output report

        def process_report_FF(): # Input report #0xFF
            if debug:
                print "process_report_FF"
    
            if length != "\x06":
                raise LengthPacketException(int("0xfd", 16), length, 6)
    
            if debug:
                print "passing..."
            self.sock.recv(ord(length) - 2)

        # Get the ID of the DATA_INPUT message
        msg_id = self.sock.recv(1)
    
        if self.debug_file:
            self.debug_file.write(msg_id)
            self.debug_file.flush()

        data = {"Report ID" : msg_id}
        try:
            if msg_id == "\x03":
                process_report_03()
            elif msg_id == "\x04":
                process_report_04()
            elif msg_id == "\x05":
                process_report_05()
            elif msg_id == "\x07":
                process_report_07()
            elif msg_id == "\x08":
                process_report_08()
            elif msg_id == "\x09":
                process_report_09()
            elif msg_id == "\x0A":
                process_report_0A()
            elif msg_id == "\x0B":
                process_report_0B()
            elif msg_id == "\x0C":
                process_report_0C()
            elif msg_id == "\x0D":
                process_report_0D()
            elif msg_id == "\x0E":
                process_report_0E()
            elif msg_id == "\x0F":
                process_report_0F()
            elif msg_id == "\x10":
                process_report_10()
            elif msg_id == "\x11":
                process_report_11()
            elif msg_id == "\x12":
                process_report_12()
            elif msg_id == "\x13":
                process_report_13()
            elif msg_id == "\x14":
                process_report_14()
            elif msg_id == "\x15":
                process_report_15()
            elif msg_id == "\x16":
                process_report_16()
            elif msg_id == "\x17":
                process_report_17()
            elif msg_id == "\x1A":
                process_report_1A()
            elif msg_id == "\x1B":
                process_report_1B()
            # Two functions for tests purpose only
            elif msg_id == "\xFD":
                process_report_FD()
            elif msg_id == "\xFF":
                process_report_FF()
        except LengthPacketException, (e):
            print e
            self.disconnect()
            sys.exit(1)
        except:
            self.disconnect()
            sys.exit(1)

        if debug:
            for x,y in data.iteritems():
                printable_y = ""
                if type(y) == type(1):
                    printable_y += "%02x " % y
                else:
                    for i in range(len(y)):
                        printable_y += "%02x " % ord(y[i])
                print "%s = %s" % (x, printable_y)

            print "--------------------------------"
    
        return data

    # TODO never tested...
    def set_idle(self, time):
        if not isinstance(time, str) or len(time) != 1:
            if debug:
                print "time has to be a 1-byte long string"
            return self.HANDSHAKE_ERR_INVALID_PARAMETER

        idle_msg = "\x02\x90" + time
        self.sock.send(idle_msg)

        if self.debug_file:
            self.debug_file.write(idle_msg)
            self.debug_file.flush()

        hs = self.sock.recv(1)
    
        if self.debug_file:
            self.debug_file.write(hs)
            self.debug_file.flush()

        return hs

    # TODO never tested...
    def set_report_type_enable(self, report_id, enable=1, raw=0, reserved=0):
        if not isinstance(report_id, str) or len(report_id) != 1:
            if debug:
                print "report_id has to be a 1-byte long string"
            return self.HANDSHAKE_ERR_INVALID_PARAMETER

        if enable != 0 and enable != 1:
            if debug:
                print "enable != {0|1}"
            return self.HANDSHAKE_ERR_INVALID_PARAMETER

        if raw != 0 and raw != 1:
            if debug:
                print "raw != {0|1}"
            return self.HANDSHAKE_ERR_INVALID_PARAMETER

        if not isinstance(reserved, int) or reserved < 0 or reserved > 255:
            if debug:
                print "reserved has to be an int (0 <= reserved <= 255)"
            return self.HANDSHAKE_ERR_INVALID_PARAMETER

        report_msg = "\x04\xA2\x06" + report_id

        # two lowest bits = 0
        reserved = reserved & 252
        byte = reserved | (raw << 1) | enable

        report_msg += chr(byte)

        self.sock.send(report_msg)

        if self.debug_file:
            self.debug_file.write(report_msg)
            self.debug_file.flush()

        hs = self.sock.recv(1)
    
        if self.debug_file:
            self.debug_file.write(hs)
            self.debug_file.flush()

        return hs

    # TODO never tested...
    def set_device_local_name(self, name="Zeemote"):
        length = len(name)

        if length > 32:
            if debug:
                print "Name length has to be lesser than 32 bytes"
            return self.HANDSHAKE_ERR_INVALID_PARAMETER

        name_msg = "\x23\xA2\x18" + chr(length) + name

        # The message has to be 35-bytes long (0x23 bytes)
        while(len(name_msg) != 35):
            name_msg += "\x00"

        self.sock.send(name_msg)

        if self.debug_file:
            self.debug_file.write(name_msg)
            self.debug_file.flush()


        # FIXME This handle a timeout exception, but a timer is more appropriate here.
        # The documentation says:
        # "If the device does not recognize this packet of this type, it should be ignored silently"
        # So make sure we're not wasting our time
        try:
            hs = self.sock.recv(1)
    
            if self.debug_file:
                self.debug_file.write(hs)
                self.debug_file.flush()
        except:
            pass

        return hs


    # FIXME doesn't work
    def set_keep_alive_interval(self, interval):
        if interval < 0 or interval > 65535:
            if debug:
                print "Interval has to be an integer between 0 and 65,535"
            return self.HANDSHAKE_ERR_INVALID_PARAMETER

        interval_msg = "\x04\xA2\x19"

        byte1 = (interval >> 8)
        byte2 = (interval & 255)

        interval_msg += chr(byte1) + chr(byte2)

        self.sock.send(interval_msg)

        if self.debug_file:
            self.debug_file.write(interval_msg)
            self.debug_file.flush()

        hs = self.sock.recv(1)
    
        if self.debug_file:
            self.debug_file.write(hs)
            self.debug_file.flush()

        return hs





