# Interaction-Design Tool for Multi-Modal Robot Communication

This project provides a prototyping tool for designing interactions with social robots. The current version is compatible with the [Pepper Robot](https://www.ald.softbankrobotics.com/en/robots/pepper) and requires a license from [Interactive-Robotics](https://www.interactive-robotics.com). 

The tool was successfully tested on ***MAC*** and ***Linux*** (it should also work on ***Windows***).

## Requirements
[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/downloads/)
[![PyQt 5.15.0](https://img.shields.io/badge/PyQt-5.x.x-brightgreen.svg)](https://pypi.org/project/PyQt5/5.9.2/)
[![PyYAML 5.x](https://img.shields.io/badge/PyYAML-5.x-blue)](https://github.com/yaml/pyyaml)
[![Spotipy 2.9.x](https://img.shields.io/badge/Spotipy-2.9.0-blue)](https://pypi.org/project/spotipy/)

To use the tool you need to do the following:

**A.** Clone the repository (e.g., in the Documents folder).

`$ cd ~/Documents`

`$ git clone https://github.com/ES-TUDelft/robot-interaction-tool.git`

**B.** Install the requirements as described in [Section I](#i-installation-guide)

**C.** Run the following script to load the tablet app on Pepper:
  
  `$ cd ~/Documents/interaction-design-tool-ir`
  
  `$ ./update_app.sh`
  
**D.** Launch the interface as follows:

`$ cd ~/Documents/interaction-design-tool-ir`

`$ python3 main_tool.py`

  * ***Note***: This repository is being updated on a regular basis. Use ***git pull*** to integrate the latest changes.

<div align="center">
  <img src="interaction_manager/ui/ui_view.png" width="750px" />
</div>

---

## Content

**I.** [Installation Guide](#i-installation-guide)

**II.** [Setting up Spotify](#ii-setting-up-spotify)

**III.** [User Manual](#iii-user-manual)

**IV.** [Citation](#iv-citation)

---

## I. Installation Guide

**TODO**

Briefly: you need Python3 and pip3, then in a terminal do:

  `$ pip3 install -r requirements.txt`

---

## II. Setting up Spotify

**TODO**

---

## III. User Manual

**TODO**

---

## IV. Citation

Please cite our work when you use this tool in your studies:

 * Elie Saad, Joost Broekens and Mark A. Neerincx (2020): An Iterative Interaction-Design Method for Multi-Modal Robot Communication. In *Proceedings of the IEEE International Conference on Robot and Human Interactive Communication (RO-MAN)*, pp. 690-697, IEEE.

       @InProceedings{Saad2020,
         author    = {Elie Saad and Joost Broekens and Mark A. Neerincx},
         booktitle = {IEEE International Conference on Robot and Human Interactive Communication (RO-MAN)},
         title     = {An Iterative Interaction-Design Method for Multi-Modal Robot Communication},
         year      = {2020},
         pages     = {690--697},
         publisher = {IEEE},
       }
