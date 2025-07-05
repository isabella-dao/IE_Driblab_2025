import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import tempfile
import pandas as pd

def test_process_all_matches_returns_dataframe(tmp_path):
    from enrichment import process_all_matches

    test_player_map = {"p1": 1}
    test_team_map = {"t1": 100, "t2": 200}

    # Create mock .json and .jsonl files with matching names
    shot_file = tmp_path / "123.json"
    tracking_file = tmp_path / "123_tracking_data.jsonl"
    shot_file.write_text(json.dumps([{
        "matchPeriod": "1H",
        "minute": 10,
        "second": 15,
        "videoTimestamp": 123.45,
        "player": {"id": "p1", "position": "Forward"},
        "team": {"id": "t1"},
        "opponentTeam": {"id": "t2"},
        "shot": {"bodyPart": "right_foot", "isGoal": False, "onTarget": True, "xg": 0.1, "xg2": 0.2},
        "possession": {"duration": 5, "startLocation": {"x": 50, "y": 34}}
    }]))

    tracking_file.write_text(json.dumps({
        "players_data": {
            "200": {"10": {"position": "GK"}}  # GK for team 200 (mapped from "t2")
        },
        "teams_data": {}
    }) + "\n" + json.dumps({
        "frame": 100,
        "period": 1,
        "Videotimestamp": 123.45,
        "data": {
            "100": [{"id": 1, "x": 50, "y": 34}],   # player "p1" mapped to id 1 on team 100
            "200": [{"id": 10, "x": 0, "y": 50}]    # goalkeeper on team 200
        }
    }))

    df = process_all_matches([str(shot_file), str(tracking_file)], test_player_map, test_team_map)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'distance_to_goal' in df.columns
