# AOG Househam Bridge
## Section control for Househam sprayers

This script listens to the 64 section PGN emitted by AgOpenGPS and sends them back over the network to the Househam TMC computer.

## Instructions for use
Plug an ethernet cable into the DHCP port of the TMC terminal, and connect it to the network on which AgOpenGPS is running.
The network will need to be on subnet 192.168.1.x, as the TMC has the IP 192.168.1.139

Ensure your computer has python installed.

Run the `AgOpenGPS Househam Bridge.exe` file.

If all goes well, it should install the dependencies and run.

If the TMC is not connected, you will see a message and the program will quit. Check your connection to the TMC and try again.

You will then need to load your vehicle in AgOpenGPS. The width and section settings will be sent automatically over the network to the Bridge and saved.
The bridge currently supports up to 16 sections.

The script is now listening to all PGNs broadcast to port `8888` and is extracting section data. This is converted into the Househam protocol and forwarded to the machine.

The COM port and machine data are saved in `config.ini`. To reset the program to defaults, open it in Notepad and set all the values to `0`.

The setting `CommsLostBehaviour`, when set to `0`, will turn off spraying if communication with AgIO is lost (this is the default).
To have the sprayer keep following its last instruction after losing communication, set this to `1`.
This is useful in bad signal areas, where network changes can sometimes cause AgIO to lock up.

### AgOpenGPS Setup

Set up the tool in AgOpenGPS to have the same section geometry as on your sprayer.


### Network Setup

Assuming your network adapter uses the 192.168.5.x AgOpenGPS subnet, you will need to set a secondary 
IP on this adapter, so that it can also talk to the 192.168.1.x subnet of the TMC



### TMC Setup

There should be no configuration required on the TMC terminal.

## Building from Development folder

- Using the bat2exe tool, select the Development folder

- Select the output directory of your choice

- It should auto-build all the files in Development into a self-contained exe file.

- Please include an updated exe with your code if you make any pull requests.

## TODO
This code was written in January 2025 based upon the Bogballe bridge.
There is always more to do, please feedback with any issues or requests.

- Validation of CRC from AOG PGNs
- Validation of acknowledgements from TMC
- Add variable rate control - wait for PGN structure to mature
