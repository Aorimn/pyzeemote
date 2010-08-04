#!/usr/bin/env python

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

# Import the class
import zeemote_listener as zl

#debug = zl.debug
debug = True


def listening_zeemote():
    moving_X = False
    moving_Y = False

    while True:
        # Waiting for a packet to be received
        packet = zeemote.listen()

        # If we receive something
        if packet:
            # Now we can check to the ID we want
            # ID 0x08, joystick movement
            if packet['Report ID'] == "\x08":
                if not moving_X:
                    if packet['X-Axis Reading'] >= "\x80" and packet['X-Axis Reading'] != "\x00":
                        if debug:
                            print "**** Moving to the left"
                    elif packet['X-Axis Reading'] < "\x80" and packet['X-Axis Reading'] != "\x00":
                        if debug:
                            print "**** Moving to the right"
                    moving_X = True
                else:
                    if packet['X-Axis Reading'] == "\x00":
                        moving_X = False

                if not moving_Y:
                    if packet['Y-Axis Reading'] >= "\x80" and packet['Y-Axis Reading'] != "\x00":
                        if debug:
                            print "**** Moving up"
                    elif packet['Y-Axis Reading'] < "\x80" and packet['Y-Axis Reading'] != "\x00":
                        if debug:
                            print "**** Moving down"
                    moving_Y = True
                else:
                    if packet['Y-Axis Reading'] == "\x00":
                        moving_Y = False
            # ID 0x07, button pressed
            elif packet['Report ID'] == "\x07":
                if packet['Key Code 1'] == "\x00":
                    if debug:
                        print "**** Button A"
                    emit_ButtonA_signal(obj)
                elif packet['Key Code 1'] == "\x01":
                    if debug:
                        print "**** Button B"
                elif packet['Key Code 1'] == "\x02":
                    if debug:
                        print "**** Button C"


# Object creation
zeemote = zl.ZeemoteControl()
# Connection
zeemote.connect()

# Listening to events
listening_zeemote()
