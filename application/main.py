import argparse
from utils import load_jsons, save_csv
from model import load_and_normalize_jsons, run_model

def main():
    parser = argparse.ArgumentParser(description="Run ML model on JSON input.")
    parser.add_argument("input_files", nargs='+', help="One or more JSON files.")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    parser.add_argument("--full-output", action="store_true", help="Include all features in the CSV.")
    args = parser.parse_args()

    try:
        data = load_jsons(args.input_files)
        shots_df = load_and_normalize_jsons(args.input_files)  # Preprocessed DataFrame
        results = run_model(shots_df, full_output=args.full_output)      # List[dict]
        save_csv(results, args.output)
        print(f"Output saved to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
