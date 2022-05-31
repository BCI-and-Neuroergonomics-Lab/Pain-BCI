from PyPav2 import Pavlok
import time

p = Pavlok()
time.sleep(3)  # short pause for Pavlok handshake
print("Pavlok connected")
p.beep(5)  # alert that device is connected

ID = input("Insert subject ID for config file: ")  # get sub#

input("Press any button to demonstrate vibration stimulus (level 6, duration 0.3s)...")
p.vibrate(6, duration_on=0.3)

input("Press any button to elicit initial shock (level 4)...")
p.shock(4)  # lowest perceptible shock

while True:
    value = int(input("Insert value for next shock (1-10): "))
    p.shock(value)
    print("Shocked at " + str(value) + " out of 10")
    end = input("End thresholding? (y/n)")
    if end == 'y':
        break
    else:
        pass

fname = ID + ".cfg"
with open(fname, 'w') as f:
    f.write("[subject-thresholding]\n")
    f.write("shock = " + str(value) + "\n")  # save pain threshold for later
