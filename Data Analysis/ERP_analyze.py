import os
import mne
import channels
import numpy as np
import matplotlib.pyplot as plt

#################
# Pre-Processing:

stims = {
    '33285': 'OVTK_StimulationId_Target',  # shock
    '33286': 'OVTK_StimulationId_NonTarget',  # vibrate
    '32775': 'OVTK_StimulationId_BaselineStart'  # baseline
}

# Establish paths for raw GDF files based on subject and condition of interest
data_path = os.path.dirname(os.path.realpath(__file__))[:-13] + os.path.join("Experiment Code", "Data")  # GDF file path
subject = "sub1"  # format is sub# (1-N)
condition = "attend"  # either attend or distract
fnames = [os.path.join( data_path, subject, subject + "-" + condition + "-" + str(i+1) + ".gdf") for i in range(6)]

amp_order = sum([channels.labels["UB20160321"], channels.labels["UB20141008"],  # order amplifiers as OpenViBE did
                 channels.labels["UB20141007"], channels.labels["UB20110715"]], [])  # (see subject summaries)
montage = mne.channels.make_standard_montage('standard_1020')

epochs_list = []
ts = -0.1  # epoch start time
te = 0.5  # epoch end time

for f in fnames:
    raw = mne.io.read_raw_gdf(f, preload=True)  # load our GDF file

    # Correct channel names using amp_order
    channel_names = {raw.ch_names[i]: amp_order[i] for i in range(len(amp_order))}  # both should be of length 64
    raw.rename_channels(channel_names)  # happens in place

    raw.set_montage(montage)  # add standard 10-20 montage information to GDF file

    # Pull the event markers from the data's annotations
    events, temp_id = mne.events_from_annotations(raw)

    # correct for TCP lag
    offset = events[0][0]
    for event in events:
        event[0] = event[0] - offset

    raw.filter(l_freq=0.1, h_freq=30.0)  # bandpass filter 0.1Hz-30Hz

    epochs_list.append(mne.Epochs(raw, events, event_id=temp_id, tmin=ts, tmax=te,
                                  preload=True, baseline=(None, 0)))  # epoch the EEG data, 100ms baseline correction

epochs_combined = mne.concatenate_epochs(epochs_list)  # combine all epochs to one object
reject_criteria = dict(eeg=100e-6)  # 100 µV
_ = epochs_combined.drop_bad(reject=reject_criteria)  # automatically drop epochs based on PPA
# fig = epochs_combined.plot()  # manually drop epochs and channels

epochs_combined["33285"].average().plot_joint()  # shock
epochs_combined["33286"].average().plot_joint()  # vibrate

"""  Stop at graphs for now...
################
# Test analysis: First, the example provided by https://neurokit2.readthedocs.io/en/latest/studies/erp_gam.html
# Selecting relevant channels (somatosensory cortex)
picks = ["C3", "C1", "Cz", "C2", "C4"]
epochs_combined = epochs_combined.pick_channels(picks)

# Transform each condition (stimulus) to array
condition1 = np.mean(epochs_combined["33285"].get_data(), axis=1)  # shock
condition2 = np.mean(epochs_combined["33286"].get_data(), axis=1)  # vibrate
condition3 = np.mean(epochs_combined["32775"].get_data(), axis=1)  # baseline

# Permutation test to find significant cluster of differences
t_vals, clusters, p_vals, h0 = mne.stats.permutation_cluster_test([condition1, condition2, condition3],
                                                                  out_type='mask', seed=111)

# Visualize
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, ncols=1, sharex=True)

times = epochs_combined.times
ax0.axvline(x=0, linestyle="--", color="black")
ax0.plot(times, np.mean(condition1, axis=0), label="Shock")
ax0.plot(times, np.mean(condition2, axis=0), label="Vibrate")
ax0.plot(times, np.mean(condition3, axis=0), label="Baseline")
ax0.legend(loc="upper right")
ax0.set_ylabel("uV")

# Difference
ax1.axvline(x=0, linestyle="--", color="black")
ax1.plot(times, condition1.mean(axis=0) - condition2.mean(axis=0))
ax1.axhline(y=0, linestyle="--", color="black")
ax1.set_ylabel("Difference")

# T-values
ax2.axvline(x=0, linestyle="--", color="black")
h = None
for i, c in enumerate(clusters):
    c = c[0]
    if p_vals[i] <= 0.05:
        h = ax2.axvspan(times[c.start],
                        times[c.stop - 1],
                        color='red',
                        alpha=0.5)
    else:
        ax2.axvspan(times[c.start],
                    times[c.stop - 1],
                    color=(0.3, 0.3, 0.3),
                    alpha=0.3)
hf = ax2.plot(times, t_vals, 'g')
if h is not None:
    plt.legend((h, ), ('cluster p-value < 0.05', ))
plt.xlabel("time (ms)")
plt.ylabel("t-values")
"""
