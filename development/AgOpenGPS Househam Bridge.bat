#!/bin/bat
# Run the AOG - Househam bridge
echo on
set pwd=%~dp0
cls

python -m pip install -r requirements.txt
cls

python main.py