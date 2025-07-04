# IE 2025 Corporate Project - Driblab xG model

Run application in Linux terminal

### System Prep (one-time only)
In the VM terminal: 
- sudo apt update && sudo apt install -y\
- sudo apt install python3-venv
- sudo apt install python3-pip

Copy the application folder into the VM, and proceed in VM terminal:
- cd application
- python3 -m venv venv
- source venv/bin/activate
- pip install --upgrade pip
- pip install -r requirements.txt

### Environment Set-Up
Every time before running the model, in the VM terminal:
- python3 -m venv venv
- source venv/bin/activate

### Running the Model
- cd application
For output file with just the predictions:
- python3 main.py inputfilename.json --output desiredoutputname.csv
For output file with features used and predictions:
- python3 main.py inputfilename.json --output desiredoutputname.csv --full-output
