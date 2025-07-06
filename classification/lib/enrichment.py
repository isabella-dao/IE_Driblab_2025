import json
import math
import os
from pathlib import Path
import pandas as pd

# Function to count defenders inside the shooting cone
def count_defenders_in_cone(shooter_x, shooter_y, defenders, goal_left, goal_right):
    def point_in_triangle(pt, v1, v2, v3):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        b1 = sign(pt, v1, v2) < 0.0
        b2 = sign(pt, v2, v3) < 0.0
        b3 = sign(pt, v3, v1) < 0.0
        return b1 == b2 == b3

    cone_vertices = [(shooter_x, shooter_y), goal_left, goal_right]
    count = 0
    for d in defenders:
       if "x" in d and "y" in d and d["x"] is not None and d["y"] is not None:
        px, py = d["x"], d["y"]
        if all(v[0] is not None and v[1] is not None for v in cone_vertices):
            if point_in_triangle((px, py), *cone_vertices):
                count += 1
    return count

# Function to check if goalkeeper is in the shot path
def is_goalkeeper_in_path(shooter_x, shooter_y, gk_x, gk_y, goal_x, goal_y, tolerance=5):
    if None in (shooter_x, shooter_y, gk_x, gk_y):
        return False
    vec_shot = (goal_x - shooter_x, goal_y - shooter_y)
    vec_gk = (gk_x - shooter_x, gk_y - shooter_y)
    cross = abs(vec_shot[0] * vec_gk[1] - vec_shot[1] * vec_gk[0])
    distance = math.hypot(*vec_shot)
    lateral_offset = cross / distance if distance else float('inf')
    return lateral_offset <= tolerance

# Function to classify field zone in 6 areas
def get_field_zone_6(x, y, attacking_right=True):
    if x is None or y is None:
        return None
    near = x > 75 if attacking_right else x < 25
    if y < 33.3:
        horiz = "left"
    elif y < 66.6:
        horiz = "center"
    else:
        horiz = "right"
    return f"{horiz}_{'near' if near else 'far'}"
    
def extract_prefix(path):
    """Get the base prefix before any underscores or extensions."""
    filename = Path(path).name
    if filename.endswith("_tracking_data.jsonl"):
        return filename.replace("_tracking_data.jsonl", "")
    elif filename.endswith(".json"):
        return filename.replace(".json", "")
    return None

def match_input_files(filepaths):
    """
    Match JSON and JSONL files based on filename prefix (not internal matchId).
    """
    file_map = {}
    for f in filepaths:
        prefix = extract_prefix(f)
        if not prefix:
            continue

        if f.endswith("_tracking_data.jsonl"):
            file_map.setdefault(prefix, {})["tracking"] = f
        elif f.endswith(".json"):
            file_map.setdefault(prefix, {})["shots"] = f

    matched = {k: v for k, v in file_map.items() if "shots" in v and "tracking" in v}

    if not matched:
        print("No matched (shots + tracking) file pairs found.")
    else:
        print(f"Matched {len(matched)} file pairs:")
        for k in matched:
            print(f"  {k}: {matched[k]['shots']} + {matched[k]['tracking']}")
    return matched
    
def process_all_matches(filepaths, player_map, team_map):
    matched_files = match_input_files(filepaths)
    all_shots = []

    for match_id, files in matched_files.items():
        print(f"Processing match_id: {match_id}")
        shots_path = files['shots']
        tracking_path = files['tracking']

        if not os.path.exists(shots_path):
            print(f"Shots file missing: {shots_path}")
            continue
        if not os.path.exists(tracking_path):
            print(f"Tracking file missing: {tracking_path}")
            continue

        # Load shots
        with open(shots_path, "r") as f:
            shots_data = json.load(f)

        if not shots_data:
            print(f"No shots found in {shots_path}")
            continue

        # Load tracking metadata
        with open(tracking_path, "r") as f:
            metadata = json.loads(f.readline())
            players_data = metadata.get("players_data", {})
            teams_data = metadata.get("teams_data", {})

        # Load tracking frames
        tracking_frames = []
        with open(tracking_path, "r") as f:
            next(f)  # skip metadata
            for line in f:
                obj = json.loads(line)
                if "Videotimestamp" in obj:
                    tracking_frames.append(obj)

        if not tracking_frames:
            print(f"No tracking frames found in {tracking_path}")
            continue

        frame_times = [f["Videotimestamp"] for f in tracking_frames]        


        # Process each shot
        for shot in shots_data:
            shot_ts = float(shot["videoTimestamp"])
            idx = min(range(len(frame_times)), key=lambda i: abs(frame_times[i] - shot_ts))
            closest_frame = tracking_frames[idx]

            player_event_id = str(shot["player"]["id"])
            team_event_id = str(shot["team"]["id"])
            opp_team_event_id = str(shot["opponentTeam"]["id"])

            player_tracking_id = player_map.get(player_event_id)
            team_tracking_id = team_map.get(team_event_id)
            opp_team_tracking_id = team_map.get(opp_team_event_id)
            
            if opp_team_tracking_id is None:
                print(f"Skipping shot due to missing team mapping for opponent {opp_team_event_id}")
                continue

            ball_x = ball_y = None
            if player_tracking_id and str(team_tracking_id) in closest_frame["data"]:
                for player in closest_frame["data"][str(team_tracking_id)]:
                    if player["id"] == player_tracking_id:
                        ball_x = player["x"]
                        ball_y = player["y"]
                        break

            goalkeeper_id = None
            team_id_key = str(opp_team_tracking_id)
            for pid, info in players_data[team_id_key].items():
                if info["position"] == "GK":
                    goalkeeper_id = int(pid)
                    break

            goalkeeper_x = goalkeeper_y = None
            if goalkeeper_id:
                for player in closest_frame["data"][team_id_key]:
                    if player["id"] == goalkeeper_id:
                        goalkeeper_x = player["x"]
                        goalkeeper_y = player["y"]
                        break

            if goalkeeper_x is not None and goalkeeper_y is not None and ball_x is not None and ball_y is not None:
                dx = ball_x - goalkeeper_x
                dy = ball_y - goalkeeper_y
                distance_to_goalkeeper = (dx**2 + dy**2)**0.5
            else:
                distance_to_goalkeeper = None

            if ball_x is not None and ball_x > 50:
                x_goal, y_goal = 105, 50
            else:
                x_goal, y_goal = 0, 50

            if ball_x is not None and ball_y is not None:
                distance_to_goal = ((x_goal - ball_x)**2 + (y_goal - ball_y)**2)**0.5
            else:
                distance_to_goal = None

            goal_x = x_goal
            goal_left_y = 30.34
            goal_right_y = 37.66

            if x_goal == 105:
                goal_left = (105, goal_left_y)
                goal_right = (105, goal_right_y)
            else:
                goal_left = (0, goal_right_y)
                goal_right = (0, goal_left_y)

            if ball_x is not None and ball_y is not None:
                a = math.hypot(goal_x - ball_x, goal_left_y - ball_y)
                b = math.hypot(goal_x - ball_x, goal_right_y - ball_y)
                c = goal_right_y - goal_left_y
                try:
                    angle_to_goal = math.acos((a**2 + b**2 - c**2) / (2 * a * b))
                except:
                    angle_to_goal = None
            else:
                angle_to_goal = None

            angle_to_goal_deg = math.degrees(angle_to_goal) if angle_to_goal is not None else None

            goalkeeper_in_shot_path = is_goalkeeper_in_path(
                shooter_x=ball_x,
                shooter_y=ball_y,
                gk_x=goalkeeper_x,
                gk_y=goalkeeper_y,
                goal_x=x_goal,
                goal_y=34,
                tolerance=5
            )

            opponent_tracking_id = str(opp_team_tracking_id)
            num_defenders_nearby = 0
            if opponent_tracking_id in closest_frame["data"]:
                for player in closest_frame["data"][opponent_tracking_id]:
                    if ball_x is not None and ball_y is not None and "x" in player and "y" in player:
                        px, py = player["x"], player["y"]
                        distance = math.hypot(ball_x - px, ball_y - py)
                        if distance <= 5:
                            num_defenders_nearby += 1

            shooter_x, shooter_y = ball_x, ball_y
            opponent_players = [
                p for p in closest_frame["data"].get(opponent_tracking_id, [])
                if p["id"] != goalkeeper_id
            ]

            try:
                defenders_in_cone = count_defenders_in_cone(
                    shooter_x, shooter_y,
                    opponent_players,
                    goal_left=goal_left,
                    goal_right=goal_right
                )
            except:
                defenders_in_cone = None

            defenders_in_box = 0
            for p in opponent_players:
                if "x" in p and "y" in p:
                    px, py = p["x"], p["y"]
                    if x_goal == 105:
                        in_area = px > 83.5 and 18 <= py <= 82
                    else:
                        in_area = px < 16.5 and 18 <= py <= 82
                    if in_area:
                        defenders_in_box += 1

            attacking_right = x_goal == 105
            field_zone_6 = get_field_zone_6(ball_x, ball_y, attacking_right=attacking_right)


            # GoalKeeper in shooting cone
            if goalkeeper_id is not None:
                goalkeeper_player = next(
                    (p for p in closest_frame["data"].get(opponent_tracking_id, []) if p["id"] == goalkeeper_id and "x" in p and "y" in p),
                    None
                )
                if goalkeeper_player:
                    gk_in_cone = count_defenders_in_cone(
                        shooter_x, shooter_y,
                        [goalkeeper_player],  
                        goal_left=goal_left,
                        goal_right=goal_right
                    ) > 0
                else:
                    gk_in_cone = None
            else:
                gk_in_cone = None


            # Count attackers in shooting cone
            shooter_x, shooter_y = ball_x, ball_y
            team_players = closest_frame["data"].get(team_tracking_id, [])
            try:
                attackers_in_cone = count_defenders_in_cone(
                    shooter_x, shooter_y,
                    team_players,
                    goal_left=goal_left,
                    goal_right=goal_right
                )
            except:
                attackers_in_cone = None

            # Distance category
            if distance_to_goal is not None:
                if distance_to_goal < 10:
                    distance_category = "very_close"
                elif distance_to_goal < 20:
                    distance_category = "close"
                elif distance_to_goal < 30:
                    distance_category = "medium"
                else:
                    distance_category = "far"
            else:
                distance_category = None

            # Angle category
            if angle_to_goal_deg is not None:
                if angle_to_goal_deg < 10:
                    angle_category = "narrow"
                elif angle_to_goal_deg < 25:
                    angle_category = "medium"
                else:
                    angle_category = "wide"
            else:
                angle_category = None

            # Pressure score
            pressure_score = (
                (num_defenders_nearby or 0) +
                (defenders_in_cone or 0) +
                (defenders_in_box or 0) +
                (1 if goalkeeper_in_shot_path else 0)
            )

            # Header or not
            bodypart = shot["shot"]['bodyPart']
            if bodypart is not None:
                header_or_not = bodypart.lower() == "head_or_other"
            else:
                header_or_not = None

            # Recoger jugadores de ambos equipos (excluyendo porteros)
            attack_team_id = str(team_tracking_id)
            defense_team_id = str(opp_team_tracking_id)

            # Excluir portero del equipo rival (ya lo tienes como goalkeeper_id)
            attacking_players = [
                p for p in closest_frame["data"].get(attack_team_id, [])
                if p.get("id") != player_tracking_id  # opcional: excluir el propio tirador
            ]

            defending_players = [
                p for p in closest_frame["data"].get(defense_team_id, [])
                if p.get("id") != goalkeeper_id
            ]

            # Combinar todos los jugadores (excepto porteros)
            all_field_players = attacking_players + defending_players

            # Calcular número de jugadores (atacantes + defensores) dentro del cono
            try:
                people_in_cone = count_defenders_in_cone(
                    shooter_x, shooter_y,
                    all_field_players,
                    goal_left=goal_left,
                    goal_right=goal_right
                )
            except:
                people_in_cone = None

            # Distance from goalkeeper to center of goal
            if goalkeeper_x is not None and goalkeeper_y is not None:
                distance_to_center_goal = math.hypot(goal_x - goalkeeper_x, 34 - goalkeeper_y)
            else:
                distance_to_center_goal = None


            # Compute goalkeeper's angle to the goal (angle visible from GK's position)
            if goalkeeper_x is not None and goalkeeper_y is not None:
                a_gk = math.hypot(goal_x - goalkeeper_x, goal_left_y - goalkeeper_y)
                b_gk = math.hypot(goal_x - goalkeeper_x, goal_right_y - goalkeeper_y)
                c_gk = abs(goal_right_y - goal_left_y)  # vertical width of goal

                try:
                    goalkeeper_angle_to_goal = math.acos((a_gk**2 + b_gk**2 - c_gk**2) / (2 * a_gk * b_gk))
                    goalkeeper_angle_to_goal_deg = math.degrees(goalkeeper_angle_to_goal)
                except:
                    goalkeeper_angle_to_goal = None
                    goalkeeper_angle_to_goal_deg = None
            else:
                goalkeeper_angle_to_goal = None
                goalkeeper_angle_to_goal_deg = None

            all_shots.append({
                "period": shot['matchPeriod'],
                "minute": shot['minute'],
                "second": shot['second'],
                "ball_x": ball_x,
                "ball_y": ball_y,
                "videoTimestamp": shot_ts,
                "Frame": closest_frame['frame'],
                "player_id": player_tracking_id,
                "team_id": team_tracking_id,
                "opp_team_id": opp_team_tracking_id,
                "position": shot['player']['position'],
                "bodypart": shot["shot"]['bodyPart'],
                "isGoal": shot["shot"]["isGoal"],
                "on_target": shot["shot"]['onTarget'],
                "xg": shot["shot"]["xg"],
                "xg2": shot["shot"]["xg2"],
                "period_frame": closest_frame["period"],
                "data": closest_frame['data'],
                "goalkeeper_x": goalkeeper_x,
                "goalkeeper_y": goalkeeper_y,
                "distance_to_goalkeeper": distance_to_goalkeeper,
                "distance_to_goal": distance_to_goal,
                "angle_to_goal": angle_to_goal,
                "angle_to_goal_degrees": angle_to_goal_deg,
                "num_defenders_nearby": num_defenders_nearby,
                "poss_duration": shot['possession']['duration'],
                "poss_start_x":shot['possession']['startLocation']['x'],
                "poss_start_y":shot['possession']['startLocation']['y'],
                "goalkeeper_in_shot_path":goalkeeper_in_shot_path,
                "defenders_in_box":defenders_in_box,
                "field_zone_6": field_zone_6,
                "distance_category": distance_category,
                "angle_category": angle_category,
                "pressure_score": pressure_score,
                "header": header_or_not,
                "defenders_in_cone": defenders_in_cone,
                "attackers_in_cone":attackers_in_cone,
                "goalkeeper_in_cone": gk_in_cone,
                "distance_to_center_goal": distance_to_center_goal,
                "goalkeeper_angle_to_goal_degrees": goalkeeper_angle_to_goal_deg,
            })
        if not all_shots:
            print("No enriched shots found for the input files. Check if they have valid data.")
            return pd.DataFrame()

    all_shots_df = pd.DataFrame(all_shots)
    return all_shots_df


