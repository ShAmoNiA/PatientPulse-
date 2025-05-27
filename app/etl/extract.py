import json, csv
from pathlib import Path
from typing import List, Dict

DATA_DIR = Path(__file__).parent.parent.parent / "data"

def load_patients() -> List[Dict]:
    with open(DATA_DIR / "patients.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_readings() -> List[Dict]:
    rows = []
    with open(DATA_DIR / "readings.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows