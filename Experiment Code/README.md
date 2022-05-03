# Information Regarding OpenViBE and the g.tech USBamp 64 Channel Configuration

Firstly, this configuration is specific to the BCI and Neuroergonomics Lab at NC State, and does not apply elsewhere.

The channel index document details how the 64 channels are grouped into 4 amplifiers each with 16 channels (denoted as A, B, C\`, and D). C\` was used to avoid confusion with the 10-20 system's C for "central". This index should never change, as even if electrodes go bad or are broken and replaced, they should be plugged back to the same spot they were removed from, resulting in no change.

As OpenViBE more-or-less randomly orders the amplifiers at startup, the safest approach is to tick the Acquisition Server box "Show device name". This will label each channel with a number and the serial number of the USBamp that it is connected to. Post-processing in Python can then properly name these channels using the index mentioned above.