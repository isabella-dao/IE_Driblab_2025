import json
import os

player_map_path = "mappings/player_event_id_to_tracking_id.json"
team_map_path = "mappings/team_event_id_to_tracking_id.json"

if not os.path.exists(player_map_path) or not os.path.exists(team_map_path):
    raise FileNotFoundError("❌ Mappings are missing. Please place them in the 'mappings/' folder.")

with open(player_map_path) as f:
    player_map = json.load(f)

with open(team_map_path) as f:
    team_map = json.load(f)
