#!/bin/bash

d=$PWD

filenames=(
  "main_qi_robot.py"
  "main_qi_engagement.py"
)

# open scripts in new tabs
for f in "${filenames[@]}"
do
  osascript -e 'tell application "Terminal"' \
            -e 'tell application "System Events" to keystroke "t" using {command down}' \
            -e 'do script "cd '"$d"'; python2 '"$f"'" in selected tab of the front window' \
            -e 'end tell'
done
