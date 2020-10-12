#!/bin/bash

# Prompt user for robot IP
read -p 'Robot IP: ' ip

echo Copying to: nao@$ip

sudo scp -r robot_manager/tablet/es_app nao@$ip:/home/nao/.local/share/PackageManager/apps/