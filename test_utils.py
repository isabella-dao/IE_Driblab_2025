import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_jsons, save_csv

def test_load_jsons_success(tmp_path):
    json_file = tmp_path / "test.json"
    json_file.write_text('{"a":1}')
    assert load_jsons([str(json_file)]) == [{"a": 1}]

def test_load_jsons_file_not_found():
    with pytest.raises(ValueError):
        load_jsons(["nonexistent.json"])

def test_load_jsons_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid JSON")
    with pytest.raises(ValueError):
        load_jsons([str(bad_file)])

def test_load_jsons_multiple_files(tmp_path):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text('{"a": 1}')
    f2.write_text('{"b": 2}')
    data = load_jsons([str(f1), str(f2)])
    assert data == [{"a": 1}, {"b": 2}]

def test_save_csv_success(tmp_path):
    out_file = tmp_path / "out.csv"
    data = [{"x": 1, "y": 2}]
    save_csv(data, str(out_file))
    assert out_file.exists()

def test_save_csv_invalid_path():
    data = [{"x": 1}]
    with pytest.raises(Exception):
        save_csv(data, "/invalid/path/out.csv")

def test_save_csv_empty_data(tmp_path):
    out_file = tmp_path / "empty.csv"
    save_csv([], str(out_file))
    assert out_file.exists()
    assert out_file.read_text().strip() == ""

def test_save_csv_non_dict_data(tmp_path):
    out_file = tmp_path / "bad.csv"
    bad_data = ["not a dict"]
    with pytest.raises(ValueError) as excinfo:
        save_csv(bad_data, str(out_file))
    assert "Input must be a list of dictionaries" in str(excinfo.value)
