# Information Regarding OpenViBE and the g.tech USBamp 64 Channel Configuration

Firstly, this configuration is specific to the BCI and Neuroergonomics Lab at NC State, and does not apply elsewhere.

The channel index document details how the 64 channels are grouped into 4 amplifiers each with 16 channels (denoted as A, B, C\`, and D). C\` was used to avoid confusion with the 10-20 system's C for "central". This index should never change, as even if electrodes go bad or are broken and replaced, they should be plugged back to the same spot they were removed from, resulting in no change.

The gamma-channel-names document details the channel names as loaded into the OpenViBE Acquisition Server. As best I can tell, when multiple amplifiers are connected, OpenViBE orders them by internal USB address. The current configuration is displayed as follows when launching the Acquisition Server:

### At launch...
* 0: 2014.10.07
* 1: 2016.03.21
* 2: 2011.07.15
* 3: 2014.10.08

### After setting the 2011 amplifier as master...
* 0: 2014.10.07
* 1: 2016.03.21
* 2: 2014.10.08
* 3: 2011.07.15

...as the master amplifier always comes last in the acquisition sequence. This replaces the previous final amplifier (2014...08) with the master (2011). This two stage configuration should be present in the log at *every launch* of the acquisition server, otherwise we cannot guarantee that the channel names file is accurate.