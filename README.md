# Classification of Pain-Related Evoked Potentials

The BCI lab is hoping to investigate the ability of pain-related evoked potentials (PREPs) as a signal for future BCIs.
Detecting and responding to injury from brain activity alone may allow for advanced systems that provide doctors and 
professionals with immediate knowledge of a signal that is traditionally hard to convey objectively. This repository 
exists to store OpenViBE scenarios, classifiers, and general scripts for the recording, detection, and analysis of PREPs
from EEG activity. 

## PiShock Stimulation
Code for the PiShock stimulus device (a Raspberry Pi Zero W + ADC + Pavlok) marks data as follows:

* Stimulus trials are generated independently of EEG data collection (either shock, vibrate, or control)
* Stimulus is presented, and timestamps are sent to OpenViBE via TCP Tagging plugin
* PiShock locally logs time of stimulation and intensity, as well as lag from TCP Tagging

During analysis, the delay (<100ms) of stimulations due to TCP Tagging is corrected for and data is analyzed