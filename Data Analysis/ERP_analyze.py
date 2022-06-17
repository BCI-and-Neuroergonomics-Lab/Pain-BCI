import os
import mne

#################
# Pre-Processing:

stims = {
    '33285': 'OVTK_StimulationId_Target',  # shock
    '33286': 'OVTK_StimulationId_NonTarget',  # vibrate
    '32775': 'OVTK_StimulationId_BaselineStart'  # baseline
}

# Establish paths for EDF files based on subject and condition of interest
data_path = os.path.dirname(os.path.realpath(__file__))[:-13] + os.path.join("Experiment Code", "Data")  # GDF file path
subjects = ["1", "2", "3"]
condition = "A"  # either Attend or Distract

montage = mne.channels.make_standard_montage('standard_1020')

epochs_list = []
ts = -0.1  # epoch start time
te = 0.5  # epoch end time

for s in subjects:  # collapse across all subjects (still with just 1 condition, attend or distract)
    filename = "sub-0" + s + "_task-" + condition + "_run-0"  # define BIDS filename here for simplicity
    fnames = [os.path.join(data_path, "sub-0" + s, "eeg", filename + str(i + 1) + "_eeg.edf") for i in range(6)]

    for f in fnames:
        raw = mne.io.read_raw_edf(f, preload=True)  # load our GDF file
        raw.set_montage(montage)  # add standard 10-20 montage information to GDF file
        # Pull the event markers from the data's annotations
        events, temp_id = mne.events_from_annotations(raw)

        # correct for TCP lag
        offset = events[0][0]
        for event in events:
            event[0] = event[0] - offset

        raw.filter(l_freq=1, h_freq=None)  # highpass filter at 1Hz
        raw.notch_filter(freqs=60)  # notch filter at 60Hz
        epochs_list.append(mne.Epochs(raw, events, event_id=temp_id, tmin=ts, tmax=te,
                                      preload=True, baseline=(None, 0)))  # epoch the data w/ 100ms baseline correction

epochs_combined = mne.concatenate_epochs(epochs_list)  # combine all epochs to one object
reject_criteria = dict(eeg=100e-6)  # 100 µV
_ = epochs_combined.drop_bad(reject=reject_criteria)  # automatically drop epochs based on PPA

epochs_combined["33285"].average().plot_joint()  # shock
epochs_combined["33286"].average().plot_joint()  # vibrate
"""
# ICA test
orig = raw.copy()
ica = mne.preprocessing.ICA(n_components=20, random_state=97, max_iter=800)
ica.fit(raw)
ica.plot_sources(raw, show_scrollbars=False)
#ica.apply(raw)
ica.plot_overlay(raw, exclude=ica.exclude)
"""