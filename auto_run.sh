#!/bin/bash

cd /home/soarce/SoarceMotorControl
git fetch 
git pull
arduino-cli compile fiber_factory_v4/fiber_factory_v4.ino --fqbn arduino:avr:uno
arduino-cli upload fiber_factory_v4/fiber_factory_v4.ino --fqbn arduino:avr:uno -p /dev/ttyACM0
python3 /home/soarce/SoarceMotorControl/tui.py