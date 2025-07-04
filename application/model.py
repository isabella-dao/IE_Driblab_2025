import json
import pandas as pd
from pathlib import Path
import os
import math
import glob
from enrichment import process_all_matches

import joblib

def prepare_data_for_prediction(all_shots_df):
    excluded_features = [
        'Frame','player_id', 'team_id', 'opp_team_id', 'videoTimestamp', 'period_frame',
        'period', 'minute', 'second', 'ball_x', 'ball_y', 'goalkeeper_x', 'goalkeeper_y',
        'poss_start_y','xg', 'xg2', 'position',
        'data','on_target','angle_to_goal',
    ]

    # Drop excluded columns
    df = all_shots_df.drop(columns=excluded_features, errors='ignore')

    # Convert types if needed
    if 'goalkeeper_in_cone' in df.columns:
        df['goalkeeper_in_cone'] = df['goalkeeper_in_cone'].astype(bool)
    else:
        raise ValueError("Missing expected column 'goalkeeper_in_cone'. Make sure enrichment step worked correctly.")

    # Features your model expects
    features = [
        'distance_to_goal', 'angle_to_goal_degrees', 'distance_to_goalkeeper',
        'goalkeeper_angle_to_goal_degrees', 'distance_to_center_goal', 'num_defenders_nearby',
        'defenders_in_box', 'defenders_in_cone', 'poss_start_x', 'poss_duration',
        'attackers_in_cone', 'distance_category', 'angle_category',
        'goalkeeper_in_shot_path', 'goalkeeper_in_cone'
    ]

    # Optionally drop rows with missing values (or handle missing values as needed)
    df = df.dropna(subset=features)

    # Select only the features for prediction
    X_pred = df[features]

    return X_pred

def run_model(model_path, X_pred, full_output=False):
    """
    Accepts a data frame.
    Returns a list of dicts including predictions.
    """
    model = joblib.load(model_path)
    # Run predictions
    predictions = model.predict(X_pred)

    if full_output:
        result_df = X_pred.copy()
        result_df['predictions'] = predictions
        return result_df
    else:
        return [{'predictions': float(p)} for p in predictions]
