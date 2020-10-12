#!/bin/bash

# Prompt user for robot IP
read -p 'Robot IP: ' ip

echo Copying to: nao@$ip

sudo scp -r robot_manager/worker/irc/rom_modified/optional/*.py nao@$ip:/home/nao/launcher/rom/rom_naoqi/rom/optional/
sudo scp -r robot_manager/worker/irc/rom_modified/rom/*.py nao@$ip:/home/nao/launcher/rom/rom_naoqi/rom/