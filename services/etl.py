import json
import csv
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any

async def extract_patients(patients_file: str) -> list[dict[str, Any]]:
    with open(patients_file, 'r') as f:
        return json.load(f)

async def extract_readings(readings_file: str) -> list[dict[str, Any]]:
    with open(readings_file, 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

async def run_etl(db: AsyncSession, patients_file: str, readings_file: str) -> None:
    raw_pats = await extract_patients(patients_file)
    raw_reads = await extract_readings(readings_file)
