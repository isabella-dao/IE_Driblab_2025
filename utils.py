import json
import pandas as pd

def load_jsons(filepaths):
    data = []
    for path in filepaths:
        try:
            with open(path) as f:
                if path.endswith(".jsonl"):
                    for line in f:
                        data.append(json.loads(line))
                else:
                    data.append(json.load(f))
        except Exception as e:
            raise ValueError(f"Failed to load {path}: {e}")
    return data

def save_csv(results, out_path):
    if isinstance(results, pd.DataFrame):
        df = results
    elif isinstance(results, list) and all(isinstance(r, dict) for r in results):
        df = pd.DataFrame(results)
    else:
        raise ValueError("Input must be a list of dictionaries or a DataFrame")

    try:
        df = pd.DataFrame(results)
        df.to_csv(out_path, index=False)
    except Exception as e:
        raise IOError(f"Could not write CSV to {out_path}: {e}")
