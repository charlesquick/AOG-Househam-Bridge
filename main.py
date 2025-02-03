'''
Section control only, no variable rate yet - CQ 3/2/25
'''

import socket
import ctypes
import time
from configparser import ConfigParser

# Declarations
localIP = ""
localPort = 8888
bufferSize = 256
HousehamPort = 6665
HousehamIP = '192.168.1.139'
AOGServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
HousehamServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

config = ConfigParser()
config.read('config.ini')
try:
    secnum = config.getint('main', 'secnum')
    secwidth = config.getfloat('main', 'secwidth')
    commsLostBehaviour = config.getint('main', 'CommsLostBehaviour')    # If true, stop spreader output on socket timeout
except:
    print("no config file!")
    while True:
            continue
activeSections = 0
activeSectionsLast = 0
AOGversion = 0
com = config.get('main', 'com')

sections = ['0'] * 64
oldSections = ['0'] * 64
speed = 0.0

portExists = False
validConf = True
AgIOSaysHello = False
socket_timeout = False
newDataFlag = False

def extractdata(input):
    global newDataFlag

    if (input[3:4].hex()) == 'eb':  # SectionDimensions PGN
        global secwidth, validConf
        secnum = int(input[37:38].hex(), 16)
        print("Section Configuration Received")
        print(secnum, " sections")
        validConf = True

        config.set('main', 'secnum', str(secnum))
        with open('config.ini', 'w') as f:
            config.write(f)
        newDataFlag = True
        return

    if (input[3:4].hex()) == 'c8':  # AgIO Hello PGN
        global AgIOSaysHello, AOGversion
        AOGversion = int(input[5:6].hex(), 16)
        AgIOSaysHello = True
        newDataFlag = True
        return

def extractSectionData(input):
    global sections
    global activeSections
    global newDataFlag
    newDataFlag = True
    byte_slice = input[5:13]
    sectBits = f'{int(byte_slice[::-1].hex(), 16):0>64b}'[::-1]
    sections = list(sectBits)
    activeSections = sections.count('1')

def checksum(input):
    hexList = []
    for x in input:
        hexList.append(hex(ord(x)))     # hex of the int of the character
    out = hexList[0]
    for i in range(1, len(hexList)):
        out = hex(int(out, 16) ^ int(hexList[i], 16))   # XOR the ints together in base16 then convert to hex
    return out[2:].upper()

def sendSections():
    global sections, oldSections
    if oldSections != sections:
        oldSections = sections
        outputlist = ['M', ',']
        if activeSections > 0:
            outputlist.append('1')
        else:
            outputlist.append('0')
        for sect in sections[0:secnum]:
            outputlist.append(str(sect))
        sectionoutput = ''.join(outputlist)
        sectionoutput += ','
        chk = checksum(sectionoutput)
        sectionoutput = "$" + sectionoutput + '*' + chk + '\r\n'
        HousehamServerSocket.send(sectionoutput.encode())
        print(sectionoutput)

def getUDPdata():
    try:
        bytesAddressPair = AOGServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
    except socket.timeout:
        if not commsLostBehaviour:
            global speed, sections, activeSections, AgIOSaysHello, socket_timeout
            speed = 0
            sections = [0] * 64
            activeSections = 0
        AgIOSaysHello = False
        socket_timeout = True
        return
    if (message[3:4].hex()) in ('64', 'fe', 'ef'):    # Keep the execution path for these PGN short, else it clogs everything up.
        return
    if (message[3:4].hex()) == 'e5':    # Is it the 64 section PGN?
        extractSectionData(message)
        return
    if (message[3:4].hex()) in ('eb', 'c8'):
        extractdata(message)            # Any other PGNs get parsed here
        return

def flush_socket():
    AOGServerSocket.setblocking(False)
    while True:
        try:
            data = AOGServerSocket.recv(1024)
            if not data:
                break
        except BlockingIOError:
            AOGServerSocket.setblocking(True)
            break


# Setup
print("CSEQ Technologies LTD")
print("AOG-Househam Bridge \n")
AOGServerSocket.bind((localIP, localPort))
try:
    HousehamServerSocket.connect((HousehamIP, HousehamPort))
except:
    errmsg = "Cannot connect to the Househam TMC. Check your connections and re-open"
    title = 'AOG-Househam Bridge'
    ctypes.windll.user32.MessageBoxW(0, errmsg, title, 0x1000 | 0x30)
    exit()

if validConf:
    print("Using saved machine configuration:")
    print("     ", secnum, " sections, each", secwidth, " cm")
    print("     Total width:", secwidth / 100 * secnum)

print("\nChecking connection to AgIO...")
AOGServerSocket.settimeout(10)
while not AgIOSaysHello:
    getUDPdata()
    if socket_timeout:
        print("Not connected to AgIO")
        socket_timeout = False

if AgIOSaysHello:
    print("Connected to AgIO")
    print("AgOpenGPS Version: ", AOGversion / 10)
    if AOGversion < 56:
        print("\nWARNING \nThis version of AgOpenGPS is not supported! Some features may not work as intended. "
              "\nConsider upgrading to version 5.7 or newer.")
flush_socket()
AOGServerSocket.settimeout(3)

try:
    while True:             # main loop
        getUDPdata()
        if newDataFlag:
            newDataFlag = False
            if validConf:
                sendSections()
            if socket_timeout:
                print("Not connected to AgIO")
                errmsg = "Lost Communication to AgIO!"
                title = 'AOG-Househam Bridge'
                ctypes.windll.user32.MessageBoxW(0, errmsg, title, 0x1000 | 0x30)
                while not AgIOSaysHello:
                    getUDPdata()
                if AgIOSaysHello:
                    print("Connected to AgIO")
                    socket_timeout = False
                    flush_socket()

except:
    errmsg = "Something went wrong! Press ok to quit. Please re-open the app."
    title = 'AOG-Househam Bridge'
    ctypes.windll.user32.MessageBoxW(0, errmsg, title, 0x1000 | 0x30)
    exit()
