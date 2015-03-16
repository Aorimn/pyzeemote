Pyzeemote is a python class, which provides access to the Zeemote
Controller Protocol (ZCP) - version 1.2. The class provides support for
establishing a Bluetooth connection to a Zeemote JS1 device and
receiving status informations from the device. Specifically, the class
can receive messages indicating the status of the Joystick and the
Buttons on the device. The class was developed and tested in the
context of a project to provide Zeemote based control to the Canola2
media player.

The class as provided can parse a useful subset of ZCP messages, however
some of the messages requires further implementation and tests. Also,
communications to the Zeemote device has not been implemented and
tested successfully to date (2010-08-05).

See youtube link below for a demonstration of pyzeemote used to control
Canola2.

Links:
http://www.zeemote.com
http://openbossa.indt.org/canola/
http://www.youtube.com/watch?v=CbaHl47w5Xo