#!/bin/bash

d=$PWD

filenames=(
  "main_robot.py"
  "main_engagement.py"
)

# open scripts in new tabs
for f in "${filenames[@]}"
do
  gnome-terminal --tab -- sh -c "cd '$d'; python3 '$f'"
done
