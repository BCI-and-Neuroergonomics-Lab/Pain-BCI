import os
import mne
import channels

stims = {
    '32769': 'OVTK_StimulationId_ExperimentStart',
    '33285': 'OVTK_StimulationId_Target',
    '33286': 'OVTK_StimulationId_NonTarget',
    '32775': 'OVTK_StimulationId_BaselineStart'
}

# Establish paths for raw GDF files based on subject and condition of interest
data_path = os.path.dirname(os.path.realpath(__file__))[:-13] + "Experiment Code\\Data"  # path to GDF files
subject = "sub1"  # format is sub# (1-N)
condition = "attend"  # or distract
fnames = [data_path + "\\" + subject + "\\" + subject + "-" + condition + "-" + str(i+1) + ".gdf" for i in range(6)]

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

    raw.filter(l_freq=0.1, h_freq=10.0)  # bandpass filter 0.5Hz-10Hz

    epochs_list.append(mne.Epochs(raw, events, event_id=temp_id, tmin=ts, tmax=te,
                                  preload=True, baseline=(ts, te)))  # epoch the EEG data

epochs_combined = mne.concatenate_epochs(epochs_list)  # combine all epochs to one object
reject_criteria = dict(eeg=100e-6)  # 100 µV
_ = epochs_combined.drop_bad(reject=reject_criteria)  # automatically drop epochs based on PPA

s = epochs_combined['33285'].average()  # average all shock trials
v = epochs_combined['33286'].average()  # average all vibrate trials
b = epochs_combined['32775'].average()  # average all baseline trials

evokeds = dict(shock=s, vibrate=v, baseline=b)
mne.viz.plot_compare_evokeds(evokeds, combine='mean')
