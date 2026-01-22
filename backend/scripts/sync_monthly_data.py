import glob
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# Load env from parent directory
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")

# Configuration
DATASETS = {
    "api_data_aadhar_enrolment": {
        "resource_id": "ecd49b12-3084-4521-8f7e-ca8bf72069ba",
        "legacy_folder": "api_data_aadhar_enrolment",
    },
    "api_data_aadhar_demographic": {
        "resource_id": "19eac040-0b94-49fa-b239-4f2fd8677d53",
        "legacy_folder": "api_data_aadhar_demographic",
    },
    "api_data_aadhar_biometric": {
        "resource_id": "65454dab-1517-40a3-ac1d-47d4dfe6891c",
        "legacy_folder": "api_data_aadhar_biometric",
    },
}

BASE_DATA_DIR = project_root / "data"


def normalize_date_vectorized(series):
    """
    Fast vectorized date parsing.
    Tries DD-MM-YYYY first, then falls back to ISO.
    """
    # Try primary format (Indian Standard: DD-MM-YYYY)
    dates = pd.to_datetime(series, format="%d-%m-%Y", errors="coerce")

    # Fill failures with secondary format (ISO: YYYY-MM-DD)
    if dates.isna().any():
        mask = dates.isna()
        dates[mask] = pd.to_datetime(series[mask], format="%Y-%m-%d", errors="coerce")

    return dates


def migrate_existing_data():
    """
    Reads existing legacy CSVs and reorganizes them into data/{dataset}/{year}/{month}.csv
    """
    print("🚀 Starting Optimized Migration...")

    for dataset_name, config in DATASETS.items():
        legacy_path = BASE_DATA_DIR / config["legacy_folder"]
        if not legacy_path.exists():
            print(f"⚠️  Legacy folder not found for {dataset_name}: {legacy_path}")
            continue

        csv_files = glob.glob(str(legacy_path / "*.csv"))
        # Filter out files that look like partitioned chunks (digits only) to avoid re-processing
        csv_files = [f for f in csv_files if not Path(f).stem.isdigit()]

        if not csv_files:
            print(f"⚠️  No legacy CSV files found in {legacy_path}")
            continue

        print(f"📦 Processing {len(csv_files)} files for {dataset_name}...")

        for file_path in csv_files:
            print(f"   Reading {Path(file_path).name}...", end="\r")
            try:
                # Read chunks to handle large files
                chunk_size = 100000  # Increased chunk size for speed
                for df in pd.read_csv(
                    file_path, chunksize=chunk_size, low_memory=False
                ):
                    # Strip whitespace from columns
                    df.columns = df.columns.str.strip()

                    if "date" not in df.columns:
                        continue

                    # FAST Vectorized Date Parsing
                    df["date_obj"] = normalize_date_vectorized(df["date"])
                    df = df.dropna(subset=["date_obj"])  # Drop rows with invalid dates

                    if df.empty:
                        continue

                    df["year"] = df["date_obj"].dt.year
                    df["month"] = df["date_obj"].dt.month

                    # Group by Year and Month
                    groups = df.groupby(["year", "month"])

                    for (year, month), group in groups:
                        # Write back to the SAME legacy folder structure, but in year subfolders
                        # e.g. data/api_data_aadhar_biometric/2024/01.csv
                        year_dir = legacy_path / str(year)
                        if not year_dir.exists():
                            year_dir.mkdir(parents=True, exist_ok=True)

                        month_file = year_dir / f"{int(month):02d}.csv"

                        # Columns to save (exclude temp cols)
                        cols_to_save = [
                            c
                            for c in df.columns
                            if c not in ["date_obj", "year", "month"]
                        ]

                        if month_file.exists():
                            # Append
                            group[cols_to_save].to_csv(
                                month_file, mode="a", header=False, index=False
                            )
                        else:
                            # Create new
                            group[cols_to_save].to_csv(month_file, index=False)

            except Exception as e:
                print(f"\n   ❌ Error processing {file_path}: {e}")

        print(f"\n✅ Finished processing {dataset_name}")


def fetch_incremental_data(days_back=30):
    """
    Fetches recent data from API and saves to monthly folders.
    """
    if not DATA_GOV_API_KEY:
        print("❌ Error: DATA_GOV_API_KEY not found in .env")
        return

    print(f"🔄 Fetching data for the last {days_back} records (simulated)...")

    # NOTE: Since the API offset strategy is complex, for this 'sync' prototype
    # we will fetch the latest 10,000 records as a proof of concept.
    # In production, use the 'offset' logic from the original sync_data.py

    for dataset_name, config in DATASETS.items():
        print(f"   Fetching {dataset_name}...")
        resource_id = config["resource_id"]
        url = f"https://api.data.gov.in/resource/{resource_id}"

        params = {
            "api-key": DATA_GOV_API_KEY,
            "format": "json",
            "limit": 5000,  # Fetch top 5000 recent
            # "sort[date]": "desc" # API might not support direct date sort efficiently
        }

        try:
            resp = requests.get(url, params=params)
            data = resp.json()

            if data.get("status") != "ok":
                print(f"   ⚠️ API Error: {data.get('message')}")
                continue

            records = data.get("records", [])
            if not records:
                print("   ⚠️ No records found.")
                continue

            df = pd.DataFrame(records)

            # Normalize Date
            df["date_obj"] = normalize_date_vectorized(df["date"])
            df = df.dropna(subset=["date_obj"])

            df["year"] = df["date_obj"].dt.year
            df["month"] = df["date_obj"].dt.month

            # Save
            groups = df.groupby(["year", "month"])
            for (year, month), group in groups:
                year_dir = BASE_DATA_DIR / dataset_name / str(year)
                year_dir.mkdir(parents=True, exist_ok=True)
                month_file = year_dir / f"{int(month):02d}.csv"

                cols_to_save = [
                    c for c in df.columns if c not in ["date_obj", "year", "month"]
                ]

                # Deduplication Strategy: Read existing, append, drop duplicates
                if month_file.exists():
                    existing = pd.read_csv(month_file)
                    combined = pd.concat([existing, group[cols_to_save]])
                    combined = combined.drop_duplicates()
                    combined.to_csv(month_file, index=False)
                else:
                    group[cols_to_save].to_csv(month_file, index=False)

            print(f"   ✅ Synced {len(records)} records.")

        except Exception as e:
            print(f"   ❌ Fetch failed: {e}")


def upload_to_release():
    """
    Uploads generated CSV files to GitHub Release 'dataset-latest'.
    Requires 'gh' CLI tool and GITHUB_TOKEN.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("ℹ️  GITHUB_TOKEN not found. Skipping release upload.")
        return

    print("🚀 Uploading to GitHub Release 'dataset-latest'...")

    try:
        # Check if gh CLI is available
        subprocess.run(["gh", "--version"], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  GitHub CLI (gh) not installed. Skipping upload.")
        return

    # Create release if not exists
    try:
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                "dataset-latest",
                "--title",
                "Latest Monthly Dataset",
                "--notes",
                f"Auto-generated update: {datetime.now().strftime('%Y-%m-%d')}",
                "--prerelease=false",
                "--latest=true",
            ],
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        pass  # Release likely exists

    # Find and upload files modified/created in this run
    # For simplicity, we scan all partitioned files. In a real run, verify timestamps.
    count = 0
    for dataset_name in DATASETS:
        dataset_path = BASE_DATA_DIR / dataset_name
        if not dataset_path.exists():
            continue

        for file_path in dataset_path.rglob("*.csv"):
            # Naming convention for asset: dataset_year_month.csv
            # data/biometric/2024/01.csv -> biometric_2024_01.csv
            year = file_path.parent.name
            month = file_path.stem  # 01
            asset_name = f"{dataset_name}_{year}_{month}.csv"

            print(f"   Uploading {asset_name}...", end="\r")
            try:
                subprocess.run(
                    [
                        "gh",
                        "release",
                        "upload",
                        "dataset-latest",
                        f"{file_path}#{asset_name}",
                        "--clobber",
                    ],
                    check=True,
                    stderr=subprocess.DEVNULL,
                )
                count += 1
            except subprocess.CalledProcessError as e:
                print(f"\n   ❌ Failed to upload {asset_name}: {e}")

    print(f"\n✅ Uploaded {count} files to GitHub Release.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        fetch_incremental_data()
        upload_to_release()
    else:
        migrate_existing_data()
        print(
            "\n💡 Tip: To fetch new data, run: python scripts/sync_monthly_data.py sync"
        )
