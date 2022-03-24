import numpy as np
import socket


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
sHOST = "192.168.50.200"  # OpenViBE ACQ IP
sPORT = 15361

print("Waiting for OpenViBE ACQ...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # open TCP socket
s.connect((sHOST, sPORT))  # connect to port
print("Socket connected (OpenViBE ACQ)")


# connect to (r)eceive port
rHOST = "192.168.50.200"  # Local IP
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

"""
-generate a stimulus every n seconds (either shock or vibe)
-when stimulus is detected by ADC (shock) or triggered (vibe)
    -send TCP marker to OV (let server bake timestamp)
    sendOVstim(ID, s, None, 4)
"""
