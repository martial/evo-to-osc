#!/usr/bin/env python3

import serial
import serial.tools.list_ports
import sys
import crcmod.predefined  # To install: pip install crcmod
from pythonosc.udp_client import SimpleUDPClient  # OSC support
import argparse  # Import argparse library

# Setup command line arguments
parser = argparse.ArgumentParser(description='Send range data from Evo sensor to OSC server.')
parser.add_argument('ip', type=str, help='IP address of the OSC server')
parser.add_argument('port', type=int, help='Port number of the OSC server')
parser.add_argument('index', type=int, help='Index to be sent with every OSC message')
args = parser.parse_args()

# Use command line arguments for OSC configuration
ip = args.ip  # IP address of the OSC server from command line argument
port = args.port  # Port number from command line argument
index = args.index  # Index from command line argument
osc_client = SimpleUDPClient(ip, port)  # Create OSC client with command line arguments

def findEvo():
    print('Scanning all live ports on this PC')
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "5740" in p[2]:
            print('Evo found on port ' + p[0])
            return p[0]
    return 'NULL'

def openEvo(portname):
    print('Attempting to open port...')
    evo = serial.Serial(portname, baudrate=115200, timeout=2)
    set_bin = (0x00, 0x11, 0x02, 0x4C)
    evo.flushInput()
    evo.write(set_bin)
    evo.flushOutput()
    print('Serial port opened')
    return evo

def get_evo_range(evo_serial):
    crc8_fn = crcmod.predefined.mkPredefinedCrcFun('crc-8')
    data = evo_serial.read(1)
    if data == b'T':
        frame = data + evo_serial.read(3)
        if frame[3] == crc8_fn(frame[0:3]):
            rng = frame[1] << 8
            rng = rng | (frame[2] & 0xFF)
        else:
            return "CRC mismatch. Check connection or make sure only one program access the sensor port."
    else:
        return "Waiting for frame header"

    if rng == 65535:
        dec_out = float('inf')
    elif rng == 1:
        dec_out = float('nan')
    elif rng == 0:
        dec_out = -float('inf')
    else:
        dec_out = rng / 1000.0
    return dec_out

if __name__ == "__main__":
    print('Starting Evo data streaming')
    port = findEvo()

    if port == 'NULL':
        print("Sorry couldn't find the Evo. Exiting.")
        sys.exit()
    else:
        evo = openEvo(port)

    while True:
        try:
            range_data = get_evo_range(evo)
            print(range_data)
            # Send range data along with index over OSC
            osc_client.send_message("/evo/range", [index, range_data])
        except serial.serialutil.SerialException:
            print("Device disconnected (or multiple access on port). Exiting...")
            break

    evo.close()
    sys.exit()
