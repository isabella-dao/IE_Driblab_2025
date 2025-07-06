import json
import pandas as pd
from pathlib import Path
import os
import math
import glob
from lib.enrichment import process_all_matches

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

    # Features your model expects
    features = [
        'distance_to_goal', 'angle_to_goal_degrees', 'distance_to_goalkeeper',
        'goalkeeper_angle_to_goal_degrees', 'distance_to_center_goal', 'num_defenders_nearby',
        'defenders_in_box', 'defenders_in_cone', 'poss_start_x', 'poss_duration',
        'attackers_in_cone', 'distance_category', 'angle_category',
        'goalkeeper_in_shot_path', 'goalkeeper_in_cone'
    ]

    # Check for missing columns
    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for prediction: {missing}")

    # Type conversion
    df['goalkeeper_in_cone'] = df['goalkeeper_in_cone'].astype(bool)

    # Optionally drop rows with missing values (or handle missing values as needed)
    df = df.dropna(subset=features)

    # Select only the features for prediction
    # Ensure 'id' is present
    if 'id' not in all_shots_df.columns:
        raise ValueError("'id' column is missing from input data.")

    X_pred = df[features].copy()
    X_pred.insert(0, 'id', all_shots_df['id'].values)

    return X_pred

def run_model(MODEL_PATH, X_pred, full_output=False):
    """
    Accepts a data frame.
    Returns a list of dicts including predictions.
    """
    model = joblib.load(MODEL_PATH)
    # Run predictions
    predictions = model.predict(X_pred.drop(columns=['id']))

    if full_output:
        result_df = X_pred.copy()
        result_df['predictions'] = predictions
        # Ensure 'id' is first column
        cols = result_df.columns.tolist()
        if cols[0] != 'id':
            cols.remove('id')
            cols = ['id'] + cols
            result_df = result_df[cols]
        return result_df
    else:
        return [{'id': row['id'], 'predictions': float(pred)} for row, pred in zip(X_pred.to_dict('records'), predictions)]
