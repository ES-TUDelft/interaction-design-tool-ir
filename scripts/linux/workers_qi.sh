#!/bin/bash

d=$PWD

filenames=(
  "main_qi_robot.py"
  "main_qi_engagement.py"
)

# open scripts in new tabs
for f in "${filenames[@]}"
do
  gnome-terminal --tab -- sh -c "cd '$d'; python2 '$f'"
done