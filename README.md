# IE 2025 Corporate Project - Driblab xG model

Classify footbal shots from a Linux terminal. 

### System Prep (one-time only)
In the VM terminal: 

```
sudo apt update
```

```
sudo apt install python3-venv python3-pip
```

Copy the application folder into the VM, and proceed in VM terminal:

```
cd classification
```

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
pip install -r lib/requirements.txt
```

### Environment Set-Up
Every time before running the model, in the VM terminal:

```
source venv/bin/activate
```

### Running the Model

```
cd classification
```

For output file with just the predictions:

```
python3 classify_shots.py input1.json input2.jsonl --player-map player_event_id_to_tracking_id.json --team-map team_event_id_to_tracking_id.json --output desiredname.csv
```

For output file with features used and predictions:

```
python3 classify_shots.py input1.json input2.jsonl --player-map player_event_id_to_tracking_id.json --team-map team_event_id_to_tracking_id.json --output desiredname.csv --full-output
```
