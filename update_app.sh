#!/bin/bash

# Prompt user for robot IP
read -p 'Robot IP: ' ip

echo Copying to: nao@$ip

sudo scp -r robot_manager/pepper/hre_dialog nao@$ip:/home/nao/.local/share/PackageManager/apps/