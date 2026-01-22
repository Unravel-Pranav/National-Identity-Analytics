"""
Data Pipeline Module
Handles loading, cleaning, and feature engineering for Aadhaar datasets.
"""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

# Try to import fuzzy matching library
try:
    from rapidfuzz import fuzz, process

    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    FUZZY_MATCHING_AVAILABLE = False
    import warnings

    warnings.warn(
        "rapidfuzz not installed. Using fallback state matching. "
        "For better performance, install with: pip install rapidfuzz",
        ImportWarning,
    )


# Master list of valid Indian states and UTs (canonical names)
VALID_STATES = frozenset(
    [
        # 28 States
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        # 8 Union Territories
        "Andaman and Nicobar Islands",
        "Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi",
        "Jammu and Kashmir",
        "Ladakh",
        "Lakshadweep",
        "Puducherry",
    ]
)

# Manual override dictionary for specific cases (takes precedence over fuzzy matching)
# Use this for historical names, common typos, or ambiguous cases
MANUAL_STATE_OVERRIDES: Dict[str, str] = {
    # Historical names
    "Orissa": "Odisha",
    "Uttaranchal": "Uttarakhand",
    "Pondicherry": "Puducherry",
    # Old UT names (before 2020 merger)
    "Dadra & Nagar Haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "Dadra and Nagar Haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu",
    "Daman and Diu": "Dadra and Nagar Haveli and Daman and Diu",
    # Common variations that might not fuzzy match well
    "Tamilnadu": "Tamil Nadu",
    "The Dadra And Nagar Haveli And Daman And Diu": "Dadra and Nagar Haveli and Daman and Diu",
}

# Invalid entries that should be filtered out (cities, pincodes, neighborhoods)
INVALID_STATES = frozenset(
    [
        "100000",
        "BALANAGAR",
        "Darbhanga",
        "Jaipur",
        "Madanapalle",
        "Nagpur",
        "Puttenahalli",
        "Raja Annamalai Puram",
    ]
)


def normalize_state_name(state_name: str) -> str:
    """
    Normalize state name by removing extra spaces, special chars, and standardizing case.

    Args:
        state_name: Raw state name from data

    Returns:
        Normalized state name with proper title case
    """
    if pd.isna(state_name):
        return ""

    # Convert to string and strip
    name = str(state_name).strip()

    # Remove extra spaces
    name = re.sub(r"\s+", " ", name)

    # Standardize special characters (& → and)
    name = name.replace("&", "and")

    # Convert to title case for consistency
    # (except for 'and' which should remain lowercase)
    name = name.title()

    # Fix 'And' back to 'and' in state names
    name = name.replace(" And ", " and ")

    return name


@lru_cache(maxsize=1024)
def fuzzy_match_state(state_name: str, threshold: int = 80) -> Optional[str]:
    """
    Dynamically match state name using fuzzy string matching.

    Args:
        state_name: Raw state name from data
        threshold: Minimum similarity score (0-100). Default 80.

    Returns:
        Matched canonical state name or None if no good match

    Examples:
        >>> fuzzy_match_state("WEST BENGAL")
        'West Bengal'
        >>> fuzzy_match_state("Westbengal")
        'West Bengal'
        >>> fuzzy_match_state("West Bangal")  # typo
        'West Bengal'
        >>> fuzzy_match_state("InvalidCity")
        None
    """
    if not state_name or not isinstance(state_name, str):
        return None

    # Check manual overrides first (highest priority)
    if state_name in MANUAL_STATE_OVERRIDES:
        return MANUAL_STATE_OVERRIDES[state_name]

    # Normalize the input
    normalized = normalize_state_name(state_name)

    # Check if already valid (exact match after normalization)
    if normalized in VALID_STATES:
        return normalized

    # Use fuzzy matching if available
    if FUZZY_MATCHING_AVAILABLE:
        # Find best match using multiple algorithms for robustness
        match = process.extractOne(
            normalized,
            VALID_STATES,
            scorer=fuzz.WRatio,  # Weighted ratio (handles case, spaces well)
            score_cutoff=threshold,
        )

        if match:
            matched_state, score, _ = match
            return matched_state
    else:
        # Fallback: case-insensitive exact match
        normalized_lower = normalized.lower()
        for valid_state in VALID_STATES:
            if valid_state.lower() == normalized_lower:
                return valid_state

    return None


def is_valid_state(state_name: str) -> bool:
    """
    Check if a state name is valid (not a city, pincode, or invalid entry).

    Args:
        state_name: State name to validate

    Returns:
        True if valid, False otherwise
    """
    if not state_name or not isinstance(state_name, str):
        return False

    # Check if in invalid list
    if state_name in INVALID_STATES:
        return False

    # Check if pure numeric (likely a pincode)
    if state_name.isdigit():
        return False

    # Check if '0' or 'nan' string
    if state_name in ("0", "nan", "NaN", "None"):
        return False

    return True


class AadhaarDataPipeline:
    """Main data pipeline for Aadhaar analytics."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._bio_df: pd.DataFrame | None = None
        self._demo_df: pd.DataFrame | None = None
        self._enrol_df: pd.DataFrame | None = None
        self._pincode_merged: pd.DataFrame | None = None
        self._state_merged: pd.DataFrame | None = None

    def load_all_data(
        self, year: int | None = None, month: int | None = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all three datasets, optionally filtered by year and month.
        Uses parallel loading for performance.
        """
        # Always reload if specific filters are requested, or if data isn't loaded yet
        if self._bio_df is None or year is not None or month is not None:
            # Helper to load and clean in one go
            def load_and_clean(dataset_name):
                raw = self._load_dataset(dataset_name, year, month)
                return self._clean_dataframe(raw)

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(load_and_clean, "api_data_aadhar_biometric"): "bio",
                    executor.submit(
                        load_and_clean, "api_data_aadhar_demographic"
                    ): "demo",
                    executor.submit(
                        load_and_clean, "api_data_aadhar_enrolment"
                    ): "enrol",
                }

                results = {}
                for future in as_completed(futures):
                    key = futures[future]
                    try:
                        results[key] = future.result()
                    except Exception as e:
                        print(f"[ERROR] Failed to load {key} data: {e}")
                        results[key] = pd.DataFrame()

            self._bio_df = results.get("bio", pd.DataFrame())
            self._demo_df = results.get("demo", pd.DataFrame())
            self._enrol_df = results.get("enrol", pd.DataFrame())

            # Add derived columns
            self._add_derived_columns()

            # Clear cached analytics since base data changed
            self._pincode_merged = None
            self._state_merged = None

        return self._bio_df, self._demo_df, self._enrol_df

    def get_available_months(self) -> List[Tuple[int, int]]:
        """Scan data directories to find available Year-Month combinations."""
        dates = set()
        # Scan one dataset structure (assuming all are synchronized)
        base_path = self.data_dir / "api_data_aadhar_biometric"

        if not base_path.exists():
            return []

        # Look for Year/Month structure
        for year_dir in base_path.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                year = int(year_dir.name)
                for month_file in year_dir.glob("*.csv"):
                    if month_file.stem.isdigit():
                        month = int(month_file.stem)
                        dates.add((year, month))

        return sorted(list(dates), reverse=True)

    def _ensure_data_exists(
        self, dataset_name: str, year: int, month: int, file_path: Path
    ) -> bool:
        """
        Check if data exists locally. If not, try to download from GitHub Release.
        Returns True if file exists (or was downloaded), False otherwise.
        """
        if file_path.exists():
            return True

        # Construct asset URL
        # Format: biometric_2024_01.csv
        dataset_key = dataset_name.replace("api_data_aadhar_", "")
        asset_name = f"{dataset_key}_{year}_{month:02d}.csv"

        # Using the raw download link from the latest release tag
        # Note: This requires the repo to be public or a token to be handled.
        # For a public repo/release:
        repo_url = "https://github.com/Arslaan/Aadhaar-Identity-Intelligence-Platform"
        download_url = f"{repo_url}/releases/download/dataset-latest/{asset_name}"

        try:
            print(f"[INFO] File missing locally: {file_path}")
            print(f"[INFO] Attempting download from: {download_url}")

            response = requests.get(download_url, stream=True, timeout=10)

            if response.status_code == 200:
                # Ensure directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"[SUCCESS] Downloaded {asset_name}")
                return True
            elif response.status_code == 404:
                print(
                    f"[WARNING] Data for {year}-{month:02d} not found in release (404)."
                )
                return False
            else:
                print(
                    f"[ERROR] Failed to download {asset_name}: Status {response.status_code}"
                )
                return False

        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            return False

    def _load_dataset(
        self,
        dataset_name: str,
        year: int | None = None,
        month: int | None = None,
    ) -> pd.DataFrame:
        """Load data from the new hierarchical structure."""
        base_path = self.data_dir / dataset_name

        if year is not None and month is not None:
            # Load specific month
            file_path = base_path / str(year) / f"{month:02d}.csv"

            # Check and fetch if missing
            self._ensure_data_exists(dataset_name, year, month, file_path)

            if file_path.exists():
                return pd.read_csv(file_path)

            # Fallback: Check if user meant monolithic file but passed params?
            # (Unlikely given the requirement, but safe to return empty)
            return pd.DataFrame()

        # Load EVERYTHING (recursive glob) — careful with memory!
        all_files = list(base_path.glob("**/*.csv"))

        if not all_files:
            return pd.DataFrame()

        return pd.concat(
            (pd.read_csv(f) for f in all_files),
            ignore_index=True,
        )

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize dataframe with dynamic fuzzy state matching.

        This method:
        1. Normalizes and fuzzy-matches state names against valid list
        2. Filters out invalid entries (cities, pincodes, etc.)
        3. Parses dates and adds temporal features
        4. Logs any unmatched states for review
        """
        df = df.copy()

        if df.empty:
            return df

        # Dynamically standardize state names using fuzzy matching
        original_states = df["state"].unique()
        matched_count = 0
        unmatched_states = []

        # Create mapping on-the-fly
        state_mapping = {}
        for state in original_states:
            if not is_valid_state(state):
                state_mapping[state] = None  # Will be filtered out
                continue

            matched = fuzzy_match_state(state)
            if matched:
                state_mapping[state] = matched
                matched_count += 1
            else:
                state_mapping[state] = None
                unmatched_states.append(state)

        # Log unmatched states (for data quality monitoring)
        if unmatched_states:
            pass  # Suppressed to reduce spam
            # import warnings
            # warnings.warn(
            #     f"{len(unmatched_states)} state names could not be matched. "
            #     f"Examples: {', '.join(unmatched_states[:3])}",
            #     UserWarning,
            # )

        # Apply mapping
        df["state"] = df["state"].map(state_mapping)

        # Filter out rows with no valid state match
        initial_rows = len(df)
        df = df[df["state"].notna()]
        filtered_rows = initial_rows - len(df)

        if filtered_rows > 0:
            pass  # Suppressed warning
            # import warnings
            # warnings.warn(
            #     f"Filtered out {filtered_rows:,} rows with invalid/unmatched states "
            #     f"({filtered_rows / initial_rows * 100:.2f}%)",
            #     UserWarning,
            # )

        # Convert date - Robust parsing
        # Try primary format (DD-MM-YYYY)
        df["date_parsed"] = pd.to_datetime(
            df["date"], format="%d-%m-%Y", errors="coerce"
        )

        # Fallback to mixed/ISO if needed
        if df["date_parsed"].isna().any():
            mask = df["date_parsed"].isna()
            # Try YYYY-MM-DD or standard pandas inference
            df.loc[mask, "date_parsed"] = pd.to_datetime(
                df.loc[mask, "date"], errors="coerce"
            )

        df["date"] = df["date_parsed"]

        # Drop rows where date is NaT
        df = df.dropna(subset=["date"])
        df = df.drop(columns=["date_parsed"])

        # Add time features
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["month_year"] = df["date"].dt.to_period("M")
        df["day_of_week"] = df["date"].dt.dayofweek
        df["week_of_year"] = df["date"].dt.isocalendar().week

        return df

    def _add_derived_columns(self) -> None:
        """Add derived columns to all dataframes."""
        # Biometric totals
        if not self._bio_df.empty and "bio_age_5_17" in self._bio_df.columns:
            self._bio_df["total_bio_updates"] = (
                self._bio_df["bio_age_5_17"] + self._bio_df["bio_age_17_"]
            )

        # Demographic totals
        if not self._demo_df.empty and "demo_age_5_17" in self._demo_df.columns:
            self._demo_df["total_demo_updates"] = (
                self._demo_df["demo_age_5_17"] + self._demo_df["demo_age_17_"]
            )

        # Enrolment totals
        if not self._enrol_df.empty and "age_0_5" in self._enrol_df.columns:
            self._enrol_df["total_enrolments"] = (
                self._enrol_df["age_0_5"]
                + self._enrol_df["age_5_17"]
                + self._enrol_df["age_18_greater"]
            )

    def get_pincode_analytics(
        self, year: int | None = None, month: int | None = None
    ) -> pd.DataFrame:
        """Get pincode-level analytics with all novel indices."""
        # Invalidate cache if specific slice is requested
        if year is not None or month is not None:
            self._pincode_merged = None

        if self._pincode_merged is not None:
            return self._pincode_merged

        bio_df, demo_df, enrol_df = self.load_all_data(year, month)

        if bio_df.empty:
            return pd.DataFrame()

        # Aggregate by pincode
        bio_pincode = (
            bio_df.groupby(["pincode", "state", "district"])
            .agg(
                {
                    "bio_age_5_17": "sum",
                    "bio_age_17_": "sum",
                    "total_bio_updates": "sum",
                    "date": "nunique",
                }
            )
            .rename(columns={"date": "bio_days"})
            .reset_index()
        )

        demo_pincode = (
            demo_df.groupby(["pincode", "state", "district"])
            .agg(
                {
                    "demo_age_5_17": "sum",
                    "demo_age_17_": "sum",
                    "total_demo_updates": "sum",
                    "date": "nunique",
                }
            )
            .rename(columns={"date": "demo_days"})
            .reset_index()
        )

        enrol_pincode = (
            enrol_df.groupby(["pincode", "state", "district"])
            .agg(
                {
                    "age_0_5": "sum",
                    "age_5_17": "sum",
                    "age_18_greater": "sum",
                    "total_enrolments": "sum",
                    "date": "nunique",
                }
            )
            .rename(columns={"date": "enrol_days"})
            .reset_index()
        )

        # Merge all
        merged = (
            bio_pincode.merge(
                demo_pincode[
                    ["pincode", "demo_age_5_17", "demo_age_17_", "total_demo_updates"]
                ],
                on="pincode",
                how="outer",
            )
            .merge(
                enrol_pincode[
                    [
                        "pincode",
                        "age_0_5",
                        "age_5_17",
                        "age_18_greater",
                        "total_enrolments",
                    ]
                ],
                on="pincode",
                how="outer",
            )
            .fillna(0)
        )

        # State validation is now handled in _clean_dataframe()
        # No need for additional filtering here

        # Calculate Novel Indices
        merged["total_updates"] = (
            merged["total_bio_updates"] + merged["total_demo_updates"]
        )

        # Identity Velocity Index (IVI)
        merged["identity_velocity_index"] = (
            merged["total_updates"] / (merged["total_enrolments"] + 1)
        ) * 100

        # Biometric Stress Index (BSI)
        merged["biometric_stress_index"] = merged["total_bio_updates"] / (
            merged["total_demo_updates"] + 1
        )

        # Youth Update Ratio
        merged["youth_update_ratio"] = (
            merged["bio_age_5_17"] + merged["demo_age_5_17"]
        ) / (merged["total_updates"] + 1)

        # Update Intensity (updates per day)
        merged["update_intensity"] = merged["total_updates"] / (merged["bio_days"] + 1)

        self._pincode_merged = merged
        return merged

    def get_state_analytics(
        self, year: int | None = None, month: int | None = None
    ) -> pd.DataFrame:
        """Get state-level analytics."""
        if year is not None or month is not None:
            self._state_merged = None

        if self._state_merged is not None:
            return self._state_merged

        bio_df, demo_df, enrol_df = self.load_all_data(year, month)

        if bio_df.empty:
            return pd.DataFrame()

        # Aggregate by state
        state_bio = (
            bio_df.groupby("state")
            .agg(
                {
                    "bio_age_5_17": "sum",
                    "bio_age_17_": "sum",
                    "total_bio_updates": "sum",
                }
            )
            .reset_index()
        )

        state_demo = (
            demo_df.groupby("state")
            .agg(
                {
                    "demo_age_5_17": "sum",
                    "demo_age_17_": "sum",
                    "total_demo_updates": "sum",
                }
            )
            .reset_index()
        )

        state_enrol = (
            enrol_df.groupby("state")
            .agg(
                {
                    "age_0_5": "sum",
                    "age_5_17": "sum",
                    "age_18_greater": "sum",
                    "total_enrolments": "sum",
                }
            )
            .reset_index()
        )

        # Merge
        state_merged = state_bio.merge(state_demo, on="state").merge(
            state_enrol, on="state"
        )

        # Calculate indices
        state_merged["total_updates"] = (
            state_merged["total_bio_updates"] + state_merged["total_demo_updates"]
        )
        state_merged["IVI"] = (
            state_merged["total_updates"] / (state_merged["total_enrolments"] + 1) * 100
        )
        state_merged["BSI"] = state_merged["total_bio_updates"] / (
            state_merged["total_demo_updates"] + 1
        )
        state_merged["youth_ratio"] = (
            state_merged["bio_age_5_17"] + state_merged["demo_age_5_17"]
        ) / (state_merged["total_updates"] + 1)

        # Stability Score (inverse of IVI, normalized)
        max_ivi = state_merged["IVI"].max()
        state_merged["stability_score"] = 100 - (state_merged["IVI"] / max_ivi * 100)

        self._state_merged = state_merged
        return state_merged

    def get_temporal_analytics(
        self, year: int | None = None, month: int | None = None
    ) -> Dict[str, pd.DataFrame]:
        """Get temporal analytics (daily, weekly, monthly)."""
        bio_df, demo_df, enrol_df = self.load_all_data(year, month)

        if bio_df.empty:
            return {
                "daily": pd.DataFrame(),
                "day_of_week": pd.DataFrame(),
                "bio_monthly": pd.Series(),
                "demo_monthly": pd.Series(),
                "enrol_monthly": pd.Series(),
            }

        # Daily aggregation
        bio_daily = bio_df.groupby("date")["total_bio_updates"].sum().reset_index()
        demo_daily = demo_df.groupby("date")["total_demo_updates"].sum().reset_index()
        enrol_daily = enrol_df.groupby("date")["total_enrolments"].sum().reset_index()

        daily = bio_daily.merge(demo_daily, on="date").merge(enrol_daily, on="date")
        daily["total_activity"] = (
            daily["total_bio_updates"]
            + daily["total_demo_updates"]
            + daily["total_enrolments"]
        )

        # Day of week aggregation
        day_of_week = (
            bio_df.groupby("day_of_week")
            .agg({"total_bio_updates": "sum"})
            .reset_index()
        )
        day_of_week = day_of_week.merge(
            demo_df.groupby("day_of_week")["total_demo_updates"].sum().reset_index(),
            on="day_of_week",
        )

        # Monthly aggregation
        bio_monthly = bio_df.groupby("month_year")["total_bio_updates"].sum()
        demo_monthly = demo_df.groupby("month_year")["total_demo_updates"].sum()
        enrol_monthly = enrol_df.groupby("month_year")["total_enrolments"].sum()

        return {
            "daily": daily,
            "day_of_week": day_of_week,
            "bio_monthly": bio_monthly,
            "demo_monthly": demo_monthly,
            "enrol_monthly": enrol_monthly,
        }

    def get_summary_stats(
        self, year: int | None = None, month: int | None = None
    ) -> Dict[str, Any]:
        """Get summary statistics for the dashboard."""
        bio_df, demo_df, enrol_df = self.load_all_data(year, month)

        if bio_df.empty:
            return {
                "total_bio_updates": 0,
                "total_demo_updates": 0,
                "total_enrolments": 0,
                "unique_pincodes": 0,
                "unique_states": 0,
                "unique_districts": 0,
                "date_range": {"start": None, "end": None},
                "avg_ivi": 0,
                "avg_bsi": 0,
                "top_state": "N/A",
                "high_stress_state": "N/A",
            }

        pincode_data = self.get_pincode_analytics(year, month)
        state_data = self.get_state_analytics(year, month)

        return {
            "total_bio_updates": int(bio_df["total_bio_updates"].sum()),
            "total_demo_updates": int(demo_df["total_demo_updates"].sum()),
            "total_enrolments": int(enrol_df["total_enrolments"].sum()),
            "unique_pincodes": int(pincode_data["pincode"].nunique()),
            "unique_states": int(bio_df["state"].nunique()),
            "unique_districts": int(bio_df["district"].nunique()),
            "date_range": {
                "start": bio_df["date"].min().strftime("%Y-%m-%d"),
                "end": bio_df["date"].max().strftime("%Y-%m-%d"),
            },
            "avg_ivi": float(pincode_data["identity_velocity_index"].mean()),
            "avg_bsi": float(pincode_data["biometric_stress_index"].mean()),
            "top_state": state_data.nlargest(1, "total_updates")["state"].iloc[0],
            "high_stress_state": state_data.nlargest(1, "BSI")["state"].iloc[0],
        }


# Singleton instance for caching
_pipeline_instance: AadhaarDataPipeline | None = None
_last_load_time: pd.Timestamp | None = None


def get_pipeline(data_dir: str = "data") -> AadhaarDataPipeline:
    """Get or create pipeline instance (singleton pattern)."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = AadhaarDataPipeline(data_dir)
    return _pipeline_instance


def refresh_pipeline(data_dir: str = "data") -> AadhaarDataPipeline:
    """Force refresh the pipeline by reloading all data from disk.

    This is useful when:
    - New data files have been added to the data folders
    - Existing CSV files have been updated
    - You want to clear cached analytics

    Returns:
        Fresh AadhaarDataPipeline instance with reloaded data.
    """
    global _pipeline_instance, _last_load_time
    _pipeline_instance = AadhaarDataPipeline(data_dir)
    _last_load_time = pd.Timestamp.now()
    return _pipeline_instance


def get_last_load_time() -> str | None:
    """Get the timestamp of when data was last loaded."""
    global _last_load_time
    if _last_load_time is not None:
        return _last_load_time.strftime("%Y-%m-%d %H:%M:%S")
    return None


def check_for_new_data(data_dir: str = "data") -> Dict[str, int]:
    """Check if there are new CSV files that haven't been loaded.

    Returns:
        Dict with counts of files per data folder.
    """
    data_path = Path(data_dir)
    folders = [
        "api_data_aadhar_biometric",
        "api_data_aadhar_demographic",
        "api_data_aadhar_enrolment",
    ]

    file_counts = {}
    for folder in folders:
        folder_path = data_path / folder
        if folder_path.exists():
            csv_files = list(folder_path.glob("*.csv"))
            file_counts[folder] = len(csv_files)

    return file_counts
