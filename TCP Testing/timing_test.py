import numpy as np
import socket
import time
import psutil
from fxpmath import Fxp
_ = time.time() - psutil.boot_time()  # first measurement is always #.0, no decimal, so discard it


def sendOVstim(ID, sock, t=None, f=4):
    # create the three pieces of the tag: [uint64 flags ; uint64 stimulation_identifier ; uint64 timestamp]
    # flags can be 1 (using fixed point time), 2 (client bakes, e.g. StimulusSender class), 4 (server bakes timestamp)
    # note also that time must be 32:32 fixed point time since boot in milliseconds (hence use of fxp)
    flags = bytearray(f.to_bytes(8, 'little'))
    event_id = bytearray(ID.to_bytes(8, 'little'))

    if t:  # if we have a timestamp, use it!
        timestamp = bytearray.fromhex(t[2:])  # trim the 0x from the front of our timestamp
        timestamp.reverse()  # reverse it to maintain little endianness
    else:  # if we have no timestamp, set to 0 (server will bake)
        timestamp = bytearray((0).to_bytes(8, 'little'))

    sock.sendall(flags)
    sock.sendall(event_id)
    sock.sendall(timestamp)  # Bad timestamp, not being read. Also causing read of GDF Incorrect? Look into this...


# connect to (s)end port
sHOST = "127.0.0.1"  # OpenViBE ACQ IP
sPORT = 15361

print("Waiting for OpenViBE ACQ...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # open TCP socket
s.connect((sHOST, sPORT))  # connect to port
print("Socket connected (OpenViBE ACQ)")


# connect to (r)eceive port
rHOST = "127.0.0.1"  # Local IP
rPORT = 5678

print("Waiting for OpenViBE...")
r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
while not connected:
    try:
        r.connect((rHOST, rPORT))
        connected = True
    except Exception as e:
        pass  # Try again
# As soon as we connect, set a starting time
start = Fxp(time.time() - psutil.boot_time(), signed=False, n_word=64, n_frac=32)
print("Socket connected (OpenViBE)")

# read the global header before receiving any streams
# all header values are uint32 - do not read 32 bytes at once, just 4 bytes at a time
# variable names sourced from documentation:
# http://openvibe.inria.fr//documentation/3.1.0/Doc_BoxAlgorithm_TCPWriter.html
header = {}
header["Version"] = np.frombuffer(r.recv(4), np.uint32)[0]
header["Endianness"] = np.frombuffer(r.recv(4), np.uint32)[0]
header["Frequency"] = np.frombuffer(r.recv(4), np.uint32)[0]
header["Channels"] = np.frombuffer(r.recv(4), np.uint32)[0]
header["Samples_per_chunk"] = np.frombuffer(r.recv(4), np.uint32)[0]
Reserved0 = np.frombuffer(r.recv(4), np.uint32)[0]
Reserved1 = np.frombuffer(r.recv(4), np.uint32)[0]
Reserved2 = np.frombuffer(r.recv(4), np.uint32)[0]


while True:
    try:
        t = np.frombuffer(r.recv(header["Samples_per_chunk"] * 8), np.float64)[-1]  # the "newest" time since scenario began
    except IndexError:
        break  # when OV is stopped, have a clean shutdown

    # capture time in seconds since boot as a 32:32 fixed point OV time format
    stamp = Fxp(time.time() - psutil.boot_time(), signed=False, n_word=64, n_frac=32)

    print("Logged time since start: ", stamp - start)
    print("OpenViBE time signal: ", t)

    if t > 10.0:  # every 10 seconds
        sendOVstim(33285, s, stamp.hex(), 1)  # send a stimulation (currently OVTK_StimulationId_Target)
        break