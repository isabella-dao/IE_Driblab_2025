import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ImportWarning)

import argparse
from lib.utils import load_jsons, save_csv
from lib.model import run_model, prepare_data_for_prediction
from lib.enrichment import match_input_files, process_all_matches
from lib.mappings import player_map, team_map
import os
MODEL_PATH = "models/best_model_lgbm.pkl"

def main():
    parser = argparse.ArgumentParser(description="Run ML model on JSON input.")
    parser.add_argument("input_files", nargs='+', help="One or more JSON files.")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    parser.add_argument("--full-output", action="store_true", help="Include all features in the CSV.")
    args = parser.parse_args()

    try:
        MODEL_PATH
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        
        data = load_jsons(args.input_files)
        all_shots_df = process_all_matches(args.input_files, player_map, team_map)  # Preprocessed DataFrame
        if all_shots_df.empty:
            raise ValueError("No valid shots found after enrichment. Cannot proceed with model.")
        
        X_pred = prepare_data_for_prediction(all_shots_df)
        results = run_model(MODEL_PATH, X_pred, full_output=args.full_output)      # List[dict]
        save_csv(results, args.output)
        print(f"Output saved to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
