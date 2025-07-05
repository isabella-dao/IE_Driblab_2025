import subprocess
import json
import os

def test_end_to_end(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps({"val": 123}))

    output_file = tmp_path / "out.csv"
    result = subprocess.run(
        ["python3", "main.py", str(input_file), "--output", str(output_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert output_file.exists()

def test_missing_output_arg(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps({"val": 123}))

    result = subprocess.run(
        ["python3", "main.py", str(input_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "usage:" in result.stderr.lower()

def test_invalid_json(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not: valid json}")

    output_file = tmp_path / "out.csv"
    result = subprocess.run(
        ["python3", "main.py", str(bad_json), "--output", str(output_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Error:" in result.stdout
    assert not output_file.exists()

def test_missing_input_file(tmp_path):
    fake_file = tmp_path / "missing.json"
    output_file = tmp_path / "out.csv"

    result = subprocess.run(
        ["python3", "main.py", str(fake_file), "--output", str(output_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Error:" in result.stdout
    assert not output_file.exists()

def test_multiple_input_files(tmp_path):
    file1 = tmp_path / "1.json"
    file2 = tmp_path / "2.json"
    file1.write_text(json.dumps({"a": 1}))
    file2.write_text(json.dumps({"b": 2}))

    output_file = tmp_path / "out.csv"
    result = subprocess.run(
        ["python3", "main.py", str(file1), str(file2), "--output", str(output_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert output_file.exists()

def test_invalid_output_path(tmp_path):
    input_file = tmp_path / "valid.json"
    input_file.write_text(json.dumps({"x": 1}))

    output_path = tmp_path / "not_a_file" / "out.csv"

    result = subprocess.run(
        ["python3", "main.py", str(input_file), "--output", str(output_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Error:" in result.stdout
    assert not output_path.exists()

