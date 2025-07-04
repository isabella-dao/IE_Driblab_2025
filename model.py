import json
import pandas as pd
from pathlib import Path
import os
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score

def load_and_normalize_jsons(filepaths):
    """
    Loads and normalizes JSON contents from one or more files.
    Parameters:
        filepaths (list of str): List of JSON file paths.
    Returns:
        pd.DataFrame: A flattened DataFrame containing all records.
    """
    all_shots = []
    for filepath in filepaths:
        if filepath.endswith(".json"):
            with open(filepath, 'r') as f:
                shots = json.load(f)
                all_shots.extend(shots)  # assuming each file has a list of shots

    shots_df = pd.json_normalize(all_shots)
    rename_dict = {
    'id': 'shot_id',
    'matchId': 'match_id',
    'matchPeriod': 'period',
    'minute': 'minute',
    'second': 'second',
    'matchTimestamp': 'matchTimestamp',
    'videoTimestamp': 'videoTimestamp',
    'relatedEventId': 'relatedEventId',
    'pass': 'pass',
    'groundDuel': 'ground_duel',
    'aerialDuel': 'aerial_duel',
    'infraction': 'infraction',
    'carry': 'carry_info',
    'type.primary': 'event_type',
    'type.secondary': 'event_subtypes',
    'location.x': 'shot_location_x',
    'location.y': 'shot_location_y',
    'team.id': 'team_id',
    'team.name': 'team_name',
    'team.formation': 'team_formation',
    'opponentTeam.id': 'opp_team_id',
    'opponentTeam.name': 'opp_team_name',
    'opponentTeam.formation': 'opp_team_formation',
    'player.id': 'player_id',
    'player.name': 'player_name',
    'player.position': 'player_pos',
    'shot.bodyPart': 'body_part',
    'shot.isGoal': 'is_goal',
    'shot.onTarget': 'on_target',
    'shot.goalZone': 'goal_zone',
    'shot.xg': 'xg',
    'shot.postShotXg': 'post_shot_xg',
    'shot.goalkeeperActionId': 'gk_action_id',
    'shot.goalkeeper.id': 'gk_id',
    'shot.goalkeeper.name': 'gk_name',
    'shot.xg2': 'xg2',
    'possession.id': 'poss_id',
    'possession.duration': 'poss_duration',
    'possession.types': 'poss_types',
    'possession.eventsNumber': 'poss_events',
    'possession.eventIndex': 'poss_event_idx',
    'possession.startLocation.x': 'poss_start_x',
    'possession.startLocation.y': 'poss_start_y',
    'possession.endLocation.x': 'poss_end_x',
    'possession.endLocation.y': 'poss_end_y',
    'possession.team.id': 'poss_team_id',
    'possession.team.name': 'poss_team_name',
    'possession.team.formation': 'poss_team_formation',
    'possession.attack.withShot': 'attack_with_shot',
    'possession.attack.withShotOnGoal': 'attack_with_shot_on_goal',
    'possession.attack.withGoal': 'attack_with_goal',
    'possession.attack.flank': 'attack_flank',
    'possession.attack.xg': 'attack_xg',
    'shot.goalkeeper': 'gk_obj'}

    shots_df.rename(columns=rename_dict, inplace=True)
    return shots_df
    
import joblib

# Load your trained model (once)
model_path = "xGmodel/test_model.pkl"

def run_model(shots_df, full_output=False):
    """
    Accepts list of dicts from one or more JSON files.
    Returns a list of dicts including predictions.
    """
    exclude_cols = [
    'is_goal', 'xg', 'xg2', 'post_shot_xg', 'attack_xg',
    'gk_obj', 'gk_id', 'gk_name', 'gk_action_id']
    
    X = shots_df.drop(columns=exclude_cols, errors='ignore').copy()
    y = shots_df['is_goal']
    
    cat_cols = X.select_dtypes(include='object').columns.tolist()
    num_cols = X.select_dtypes(include='number').columns.tolist()

    # Convert list-based categories into string representation
    for col in cat_cols:
        if X[col].apply(type).eq(list).any():
            X[col] = X[col].apply(lambda x: ','.join(x) if isinstance(x, list) else x)
    
    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)
    
    preprocessor = ColumnTransformer([
    ('num', 'passthrough', num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)])

    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_leaf=10,
        max_features='sqrt',
        random_state=42)

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', rf_model)])
   
#Skipping calibration for now because database is too small.   
    #calibrated_rf = CalibratedClassifierCV(estimator=pipeline,method='isotonic',cv=3)
    
    #calibrated_rf.fit(X_train, y_train)

    #y_train_pred = calibrated_rf.predict_proba(X_train)[:, 1]
    #y_test_pred = calibrated_rf.predict_proba(X_test)[:, 1]
    #shots_df['xg_model_rf'] = calibrated_rf.predict_proba(X)[:, 1]
    
#Adding this only to temporarily replace the calibration part.
    pipeline.fit(X_train, y_train)
    shots_df['xg_model_rf'] = pipeline.predict_proba(X)[:, 1]
    
    if full_output:
        return shots_df.to_dict(orient="records")
    
    bins = [i / 10 for i in range(11)]
    labels = [f"{round(bins[i],1)}–{round(bins[i+1],1)}" for i in range(len(bins)-1)]

    shots_df['xg_model_rf_bucket'] = pd.cut(
        shots_df['xg_model_rf'], bins=bins, labels=labels, include_lowest=True)

    xg_rf_summary = (
        shots_df.groupby('xg_model_rf_bucket', observed=True)
        .agg(
            shots=('xg_model_rf', 'count'),
            goals=('is_goal', 'sum')
        )
        .assign(
            goal_rate=lambda df: df['goals'] / df['shots'],
            shot_share=lambda df: df['shots'] / df['shots'].sum()
        )
        .reset_index())
    return xg_rf_summary.to_dict(orient="records")
