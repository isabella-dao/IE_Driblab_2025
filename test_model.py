import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import joblib
import pytest

from model import prepare_data_for_prediction, run_model

# Mock data to test model preparation and inference
def sample_enriched_data():
    return pd.DataFrame([{
        'distance_to_goal': 18.5,
        'angle_to_goal_degrees': 22.0,
        'distance_to_goalkeeper': 12.3,
        'goalkeeper_angle_to_goal_degrees': 15.1,
        'distance_to_center_goal': 3.4,
        'num_defenders_nearby': 2,
        'defenders_in_box': 4,
        'defenders_in_cone': 1,
        'poss_start_x': 45.0,
        'poss_duration': 7.0,
        'attackers_in_cone': 2,
        'distance_category': 'medium',
        'angle_category': 'medium',
        'goalkeeper_in_shot_path': True,
        'goalkeeper_in_cone': True
    }])

def test_prepare_data_for_prediction():
    enriched_df = sample_enriched_data()

    # Add fake columns to be dropped
    enriched_df['videoTimestamp'] = 123.45
    enriched_df['data'] = None

    pred_df = prepare_data_for_prediction(enriched_df)
    assert isinstance(pred_df, pd.DataFrame)
    assert 'distance_to_goal' in pred_df.columns
    assert 'videoTimestamp' not in pred_df.columns

def test_run_model_output_format():
    enriched_df = sample_enriched_data()
    X_pred = prepare_data_for_prediction(enriched_df)

    # Mock model
    from sklearn.dummy import DummyRegressor
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(X_pred, [0.5])

    model_path = "dummy_model.pkl"
    joblib.dump(dummy, model_path)

    try:
        result = run_model(model_path, X_pred)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert 'predictions' in result[0]

        result_df = run_model(model_path, X_pred, full_output=True)
        assert isinstance(result_df, pd.DataFrame)
        assert 'predictions' in result_df.columns
    finally:
        os.remove(model_path)

