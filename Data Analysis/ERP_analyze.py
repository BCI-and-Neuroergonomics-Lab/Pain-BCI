import mne

stims = {
    '32769': 'OVTK_StimulationId_ExperimentStart',
    '33285': 'OVTK_StimulationId_Target',
    '33286': 'OVTK_StimulationId_NonTarget',
    '32775': 'OVTK_StimulationId_BaselineStart'
}

montage = mne.channels.make_standard_montage('standard_1020')
fnames = []
epochs_list = []
ts = -0.3  # epoch start time
te = 0.7  # epoch end time

for f in fnames:
    raw = mne.io.read_raw_gdf(f, preload=True)  # load our GDF file
    raw.set_montage(montage)  # add standard 10-20 montage information to GDF file

    # Pull the event markers from the data's annotations
    events, temp_id = mne.events_from_annotations(raw)

    # correct for TCP lag
    offset = events[0][0]
    for event in events:
        event[0] = event[0] - offset

    raw.filter(l_freq=0.5, h_freq=10.0)  # bandpass filter 0.5Hz-10Hz
    raw.notch_filter(60.0)  # might not be needed considering tight bandpass above...

    epochs_list.append(mne.Epochs(raw, events, event_id=temp_id, tmin=ts, tmax=te,
                                  preload=True, baseline=(ts, te)))  # epoch the EEG data

epochs_combined = mne.concatenate_epochs(epochs_list)  # combine all epochs to one object
fig = epochs_combined.plot()  # manually mark channels and epochs as bad

s = epochs_combined['33285'].average()  # average all shock trials
v = epochs_combined['33286'].average()  # average all vibrate trials
b = epochs_combined['32775'].average()  # average all baseline trials

# mne.viz.plot_compare_evokeds(s, combine='mean') for average signal across all channels
# s.plot_joint() for inclusion of montage topography with signal
# s.plot() just shows all the signal with all the channels
