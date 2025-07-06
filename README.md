# IE 2025 Corporate Project - Driblab xG model

Classify footbal shots from a Linux terminal.

### Requirements

This project has been tested on Ubuntu 24.04 LTS. It should run on Windows and Mac OSX as well, with minor adjustements.

### System preparation (one-time only)

In the Linux system terminal:

```
sudo apt update
```

```
<<<<<<< HEAD
sudo apt install -y python3-venv python3-pip
```

Clone the repository with:
=======
sudo apt install python3-venv python3-pip
```

Copy the application folder into the VM, and proceed in VM terminal:
>>>>>>> 6a195e7c529cfc6be7ecfc1ce002e7cda29ab4b7

```
git clone https://github.com/isabella-dao/IE_Driblab_2025.git
```

and proceed as follows:

```
cd IE_Driblab_2025/classification
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

### Environment setup

Every time before running the model, execute in the terminal:

```
source venv/bin/activate
```

### Running the Model

```
cd classification
```

For output file with just the predictions:

```
python3 classify_shots.py shots_file.json tracking_file.jsonl --player-map player_event_id_to_tracking_id.json --team-map team_event_id_to_tracking_id.json --output desiredname.csv
```

For output file with features used and predictions:

```
python3 classify_shots.py shots_file.json tracking_file.jsonl --player-map player_event_id_to_tracking_id.json --team-map team_event_id_to_tracking_id.json --output desiredname.csv --full-output
```