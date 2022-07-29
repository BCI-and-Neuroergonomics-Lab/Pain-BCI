import os
import mne

labels = {
    "UB20160321":
    [
        "FC1",
        "P1",
        "PO3",
        "O1",
        "CP1",
        "AF3",
        "Fp1",
        "Fz",
        "AF7",
        "CPz",
        "FCz",
        "Cz",
        "C1",
        "F1",
        "AF2",
        "Fpz"
    ],

    "UB20141008":
    [
        "F7",
        "FT7",
        "T7",
        "TP7",
        "P7",
        "F5",
        "FC5",
        "C5",
        "PO7",
        "P3",
        "CP3",
        "FC3",
        "C3",
        "F3",
        "P5",
        "CP5"
    ],

    "UB20141007":
    [
        "TP8",
        "P8",
        "O10",
        "Iz",
        "O9",
        "Oz",
        "POz",
        "Pz",
        "T8",
        "FT8",
        "F8",
        "C6",
        "CP6",
        "P6",
        "PO8",
        "AF8"
    ],

    "UB20110715":
        [
        "F4",
        "P2",
        "CP2",
        "C2",
        "FC2",
        "F2",
        "AF4",
        "Fp2",
        "O2",
        "PO4",
        "P4",
        "CP4",
        "C4",
        "FC4",
        "FC6",
        "F6",
    ]
}

subjects = ["sub5"]  # format is sub# (1-N)
conditions = ["attend", "distract"]  # both possible attention conditions

# Establish paths for raw GDF files based on subject and condition of interest
data_path = os.path.dirname(os.path.realpath(__file__))[:-13] + os.path.join("Experiment Code", "Data")  # GDF file path

amp_order = sum([labels["UB20160321"], labels["UB20141008"],  # order amplifiers as OpenViBE did
                 labels["UB20141007"], labels["UB20110715"]], [])  # (see subject summaries)
fnames = []

for s in subjects:
    for condition in conditions:
        # build a list of all 6 runs for each sub-condition pair
        fnames = fnames + [os.path.join(data_path, s, s + "-" + condition + "-" + str(i + 1) + ".gdf") for i in range(6)]
        for f in fnames:
            raw = mne.io.read_raw_gdf(f)  # load our GDF file

            # Correct channel names using amp_order
            channel_names = {raw.ch_names[i]: amp_order[i] for i in range(len(amp_order))}  # both should be of length 64
            raw.rename_channels(channel_names)  # happens in place

            for i in channel_names.values():
                raw.set_channel_types({i: "eeg"})  # ensure that every channel is set to type "eeg"

            # Grab the data that we need for BIDS formatting
            run = f[-5:][:-4]
            num = s[-1:]
            task = condition[0].upper()
            BIDS_name = "sub-0" + num + "_task-" + task + "_run-0" + run + "_eeg.edf"
            print(BIDS_name)
            raw.export(BIDS_name)  # export new .edf file
