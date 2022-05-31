#!/usr/bin/env python3
from PyPav2 import Pavlok
import configparser
import numpy as np
import random
import socket
import time
import csv
import os
import automationhat
time.sleep(0.1) # Short pause after ads1015 class creation recommended
p = Pavlok()
time.sleep(3)  # short pause for Pavlok handshake
print("Pavlok connected")

ID = input("Insert subject ID: ")
path = os.path.dirname(os.path.realpath(__file__))  # get local directory


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
    sock.sendall(timestamp)


""" Experimental Constants:
This includes stimulus thresholds from pre-task thresholding
and timing parameters that should be tuned before data collection.

Also generates randomized trial list.
"""
configParser = configparser.RawConfigParser()
config = os.path.join(path, ID + ".cfg")
configParser.read(config)  # load config file

threshold = {  # stimulus thresholds, determined ahead of time
    's': int(configParser.get('subject-thresholding', 'shock')),  # read from config
    'v': 6  # currently hard-coded at 6
}
stims = ['s', 'v', 'n']
duration = 0.3  # vibration duration, seconds
ITI = 3.0  # inter-trial interval, seconds
random_delay = 3.0  # random delay after ITI, seconds
n_trials = 10  # number of trials per stimulation
log = {}  # dict to log shocks

# generate a randomized stimulus presentation array, n trials long
trials = ""
for i in stims:
    trials += (i * n_trials)
trials = list(trials)
random.shuffle(trials)
print("Trial list generated: ", trials)


""" OpenViBE TCP Connections:
This includes both receiving packets from OV (using TCP writer box)
and sending packets to OV (using Acquisition Server TCP tagging).

Note, we might not use both, but they're easy and good to have.
"""
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
# NOTE: header packet is not working, for now hard code values. Values still must be read to clear pipe though
sendOVstim(32769, s, None, 4)  # give us a value to offset later analyses with if we need (Experiment Start = 32769)
start = time.time()  # calculate a start time for internal timestamp logging
r.close()  # TCP port must be closed here, for some reason causes OV to lag at ~32s

""" Actual Experiment Code
Here we iterate through the list of trials, presenting stimulus as assigned.
After each trial, where one of [stim] were presented, we wait

ITI + some random time (from 0-random_delay seconds)

and then begin the next trial. Each trial is timestamped and sent to OV.
"""
time.sleep(ITI)  # brief pause before start of experiment
for trial in trials:
    if trial == 's':  # a shock stimulation
        print("Trial is shock")
        already_read = False
        p.shock(threshold[trial])  # call for a shock at the desired threshold
        while not already_read:  # listen to ADC to properly timestamp shock
            if automationhat.input[2].is_on():  # react if input is high (>3v)
                # timestamp the EEG data
                sendOVstim(33285, s, None, 4)  # send marker to OpenViBE ASAP (OVTK_StimulationId_Target: 33285)

                # log the shock level and time
                voltage = automationhat.analog[2].read()  # read voltage on our ADC channel
                t = time.time() - start  # log seconds since experiment start

                # log shock level and time to csv
                log[t] = voltage

                already_read = True  # prevent multiple ADC readings after the first one
                print("Shock logged")
            elif automationhat.input[2].is_off():  # ignore if input is low (<1v)
                pass

    elif trial == 'v':  # a vibrotactile stimulation
        # timestamp the EEG data
        sendOVstim(33286, s, None, 4)  # send marker to OpenViBE (OVTK_StimulationId_NonTarget: 33286)
        t = time.time() - start  # log seconds since experiment start

        # call for vibrate at the desired threshold
        p.vibrate(threshold[trial], duration_on=duration)

        # log vibrate time to csv
        log[t] = 1.0
        print("Trial is vibrate (1) and logged")

    elif trial == 'n':  # a baseline, or non-stimulation
        # timestamp the EEG data
        sendOVstim(32775, s, None, 4)  # send marker to OpenViBE (OVTK_StimulationId_BaselineStart: 32775)
        t = time.time() - start  # log seconds since experiment start

        # do nothing, since this is a baseline trial!

        # log baseline and time to csv
        log[t] = 0.0
        print("Trial is baseline (0) and logged")

    # being inter-trial interval:
    # wait ITI seconds + a random amount up to random_delay seconds
    print("Sleeping for next trial")
    time.sleep(ITI + random.uniform(0.0, random_delay))
    # then begin again

# signal end of experiment
sendOVstim(32770, s, None, 4)  # send marker to OpenViBE (OVTK_GDF_ExperimentStop: 32770)

# Log session to a local file for later reference
num = input("Insert subject number: ")
task = input("Insert task letter: ")
run = input("Insert run number: ")
fname = "sub-0" + num + "_task-" + task + "_run-0" + run + "_log"
print(log)
print(fname)
with open(fname, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerows(log.items())
print("Session logged to csv")
