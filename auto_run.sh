#!/bin/bash

cd /home/soarce/SoarceMotorControl
echo "Fetching Updates from GitHub"
git fetch 
git pull
echo "Compiling Arduino Code"
arduino-cli compile fiber_factory_v4/fiber_factory_v4.ino --fqbn arduino:avr:uno
echo "Uploading To Arduino"
arduino-cli upload fiber_factory_v4/fiber_factory_v4.ino --fqbn arduino:avr:uno -p /dev/ttyACM0
python3 /home/soarce/SoarceMotorControl/tui.py