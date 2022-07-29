import os
import mne

###############################
# Load pre-processed EEG data #
###############################

N = 5  # Total number of subjects to load (1-N)

# Path of this file + location for Data folder
data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pre-processed")

# Dictionary to store all subject's data
data = {}

# Load all N subject's data
for i in range(N):  # NOTE: this currently only functions for <10 subjects due to 0 padding
    # load all runs of both conditions (concatenated in pre-processing
    attend = os.path.join(data_path, "sub-0" + str(i + 1) + "_task-A_eeg.set")
    distract = os.path.join(data_path, "sub-0" + str(i + 1) + "_task-D_eeg.set")

    data[str(i + 1) + 'A'] = mne.io.read_raw_eeglab(attend, preload=True)
    data[str(i + 1) + 'D'] = mne.io.read_raw_eeglab(distract, preload=True)

print(data)
