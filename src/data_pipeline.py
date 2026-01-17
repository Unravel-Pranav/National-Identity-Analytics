"""
Data Pipeline Module
Handles loading, cleaning, and feature engineering for Aadhaar datasets.
"""
import pandas as pd
import numpy as np
import glob
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from functools import lru_cache
import re

# Try to import fuzzy matching library
try:
    from rapidfuzz import process, fuzz
    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    FUZZY_MATCHING_AVAILABLE = False
    import warnings
    warnings.warn(
        "rapidfuzz not installed. Using fallback state matching. "
        "For better performance, install with: pip install rapidfuzz",
        ImportWarning
    )


# Master list of valid Indian states and UTs (canonical names)
VALID_STATES = frozenset([
    # 28 States
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
    'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
    'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    # 8 Union Territories
    'Andaman and Nicobar Islands', 'Chandigarh', 
    'Dadra and Nagar Haveli and Daman and Diu',
    'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
])

# Manual override dictionary for specific cases (takes precedence over fuzzy matching)
# Use this for historical names, common typos, or ambiguous cases
MANUAL_STATE_OVERRIDES: Dict[str, str] = {
    # Historical names
    'Orissa': 'Odisha',
    'Uttaranchal': 'Uttarakhand',
    'Pondicherry': 'Puducherry',
    # Old UT names (before 2020 merger)
    'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
    'Dadra and Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
    'Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
    'Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
    # Common variations that might not fuzzy match well
    'Tamilnadu': 'Tamil Nadu',
    'The Dadra And Nagar Haveli And Daman And Diu': 'Dadra and Nagar Haveli and Daman and Diu',
}

# Invalid entries that should be filtered out (cities, pincodes, neighborhoods)
INVALID_STATES = frozenset([
    '100000', 'BALANAGAR', 'Darbhanga', 'Jaipur', 'Madanapalle', 
    'Nagpur', 'Puttenahalli', 'Raja Annamalai Puram'
])


def normalize_state_name(state_name: str) -> str:
    """
    Normalize state name by removing extra spaces, special chars, and standardizing case.
    
    Args:
        state_name: Raw state name from data
        
    Returns:
        Normalized state name with proper title case
    """
    if pd.isna(state_name):
        return ''
    
    # Convert to string and strip
    name = str(state_name).strip()
    
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)
    
    # Standardize special characters (& → and)
    name = name.replace('&', 'and')
    
    # Convert to title case for consistency
    # (except for 'and' which should remain lowercase)
    name = name.title()
    
    # Fix 'And' back to 'and' in state names
    name = name.replace(' And ', ' and ')
    
    return name


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
            score_cutoff=threshold
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
    if state_name in ('0', 'nan', 'NaN', 'None'):
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
    
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all three datasets."""
        if self._bio_df is None:
            self._bio_df = self._load_dataset("api_data_aadhar_biometric")
            self._demo_df = self._load_dataset("api_data_aadhar_demographic")
            self._enrol_df = self._load_dataset("api_data_aadhar_enrolment")
            
            # Clean and process
            self._bio_df = self._clean_dataframe(self._bio_df)
            self._demo_df = self._clean_dataframe(self._demo_df)
            self._enrol_df = self._clean_dataframe(self._enrol_df)
            
            # Add derived columns
            self._add_derived_columns()
        
        return self._bio_df, self._demo_df, self._enrol_df
    
    def _load_dataset(self, folder_name: str) -> pd.DataFrame:
        """Load all CSV files from a dataset folder."""
        folder_path = self.data_dir / folder_name
        csv_files = glob.glob(str(folder_path / "*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {folder_path}")
        return pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    
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
        
        # Dynamically standardize state names using fuzzy matching
        original_states = df['state'].unique()
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
            import warnings
            warnings.warn(
                f"{len(unmatched_states)} state names could not be matched. "
                f"Examples: {', '.join(unmatched_states[:3])}",
                UserWarning
            )
        
        # Apply mapping
        df['state'] = df['state'].map(state_mapping)
        
        # Filter out rows with no valid state match
        initial_rows = len(df)
        df = df[df['state'].notna()]
        filtered_rows = initial_rows - len(df)
        
        if filtered_rows > 0:
            import warnings
            warnings.warn(
                f"Filtered out {filtered_rows:,} rows with invalid/unmatched states "
                f"({filtered_rows/initial_rows*100:.2f}%)",
                UserWarning
            )
        
        # Convert date
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        
        # Add time features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['month_year'] = df['date'].dt.to_period('M')
        df['day_of_week'] = df['date'].dt.dayofweek
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        return df
    
    def _add_derived_columns(self) -> None:
        """Add derived columns to all dataframes."""
        # Biometric totals
        self._bio_df['total_bio_updates'] = (
            self._bio_df['bio_age_5_17'] + self._bio_df['bio_age_17_']
        )
        
        # Demographic totals
        self._demo_df['total_demo_updates'] = (
            self._demo_df['demo_age_5_17'] + self._demo_df['demo_age_17_']
        )
        
        # Enrolment totals
        self._enrol_df['total_enrolments'] = (
            self._enrol_df['age_0_5'] + 
            self._enrol_df['age_5_17'] + 
            self._enrol_df['age_18_greater']
        )
    
    def get_pincode_analytics(self) -> pd.DataFrame:
        """Get pincode-level analytics with all novel indices."""
        if self._pincode_merged is not None:
            return self._pincode_merged
        
        bio_df, demo_df, enrol_df = self.load_all_data()
        
        # Aggregate by pincode
        bio_pincode = bio_df.groupby(['pincode', 'state', 'district']).agg({
            'bio_age_5_17': 'sum', 'bio_age_17_': 'sum', 
            'total_bio_updates': 'sum', 'date': 'nunique'
        }).rename(columns={'date': 'bio_days'}).reset_index()
        
        demo_pincode = demo_df.groupby(['pincode', 'state', 'district']).agg({
            'demo_age_5_17': 'sum', 'demo_age_17_': 'sum', 
            'total_demo_updates': 'sum', 'date': 'nunique'
        }).rename(columns={'date': 'demo_days'}).reset_index()
        
        enrol_pincode = enrol_df.groupby(['pincode', 'state', 'district']).agg({
            'age_0_5': 'sum', 'age_5_17': 'sum', 'age_18_greater': 'sum',
            'total_enrolments': 'sum', 'date': 'nunique'
        }).rename(columns={'date': 'enrol_days'}).reset_index()
        
        # Merge all
        merged = bio_pincode.merge(
            demo_pincode[['pincode', 'demo_age_5_17', 'demo_age_17_', 'total_demo_updates']], 
            on='pincode', how='outer'
        ).merge(
            enrol_pincode[['pincode', 'age_0_5', 'age_5_17', 'age_18_greater', 'total_enrolments']], 
            on='pincode', how='outer'
        ).fillna(0)
        
        # State validation is now handled in _clean_dataframe()
        # No need for additional filtering here
        
        # Calculate Novel Indices
        merged['total_updates'] = merged['total_bio_updates'] + merged['total_demo_updates']
        
        # Identity Velocity Index (IVI)
        merged['identity_velocity_index'] = (
            merged['total_updates'] / (merged['total_enrolments'] + 1)
        ) * 100
        
        # Biometric Stress Index (BSI)
        merged['biometric_stress_index'] = (
            merged['total_bio_updates'] / (merged['total_demo_updates'] + 1)
        )
        
        # Youth Update Ratio
        merged['youth_update_ratio'] = (
            (merged['bio_age_5_17'] + merged['demo_age_5_17']) / 
            (merged['total_updates'] + 1)
        )
        
        # Update Intensity (updates per day)
        merged['update_intensity'] = merged['total_updates'] / (merged['bio_days'] + 1)
        
        self._pincode_merged = merged
        return merged
    
    def get_state_analytics(self) -> pd.DataFrame:
        """Get state-level analytics."""
        if self._state_merged is not None:
            return self._state_merged
        
        bio_df, demo_df, enrol_df = self.load_all_data()
        
        # Aggregate by state
        state_bio = bio_df.groupby('state').agg({
            'bio_age_5_17': 'sum', 'bio_age_17_': 'sum', 
            'total_bio_updates': 'sum'
        }).reset_index()
        
        state_demo = demo_df.groupby('state').agg({
            'demo_age_5_17': 'sum', 'demo_age_17_': 'sum', 
            'total_demo_updates': 'sum'
        }).reset_index()
        
        state_enrol = enrol_df.groupby('state').agg({
            'age_0_5': 'sum', 'age_5_17': 'sum', 'age_18_greater': 'sum',
            'total_enrolments': 'sum'
        }).reset_index()
        
        # Merge
        state_merged = state_bio.merge(state_demo, on='state').merge(state_enrol, on='state')
        
        # Calculate indices
        state_merged['total_updates'] = (
            state_merged['total_bio_updates'] + state_merged['total_demo_updates']
        )
        state_merged['IVI'] = (
            state_merged['total_updates'] / (state_merged['total_enrolments'] + 1) * 100
        )
        state_merged['BSI'] = (
            state_merged['total_bio_updates'] / (state_merged['total_demo_updates'] + 1)
        )
        state_merged['youth_ratio'] = (
            (state_merged['bio_age_5_17'] + state_merged['demo_age_5_17']) / 
            (state_merged['total_updates'] + 1)
        )
        
        # Stability Score (inverse of IVI, normalized)
        max_ivi = state_merged['IVI'].max()
        state_merged['stability_score'] = 100 - (state_merged['IVI'] / max_ivi * 100)
        
        self._state_merged = state_merged
        return state_merged
    
    def get_temporal_analytics(self) -> Dict[str, pd.DataFrame]:
        """Get temporal analytics (daily, weekly, monthly)."""
        bio_df, demo_df, enrol_df = self.load_all_data()
        
        # Daily aggregation
        bio_daily = bio_df.groupby('date')['total_bio_updates'].sum().reset_index()
        demo_daily = demo_df.groupby('date')['total_demo_updates'].sum().reset_index()
        enrol_daily = enrol_df.groupby('date')['total_enrolments'].sum().reset_index()
        
        daily = bio_daily.merge(demo_daily, on='date').merge(enrol_daily, on='date')
        daily['total_activity'] = (
            daily['total_bio_updates'] + 
            daily['total_demo_updates'] + 
            daily['total_enrolments']
        )
        
        # Day of week aggregation
        day_of_week = bio_df.groupby('day_of_week').agg({
            'total_bio_updates': 'sum'
        }).reset_index()
        day_of_week = day_of_week.merge(
            demo_df.groupby('day_of_week')['total_demo_updates'].sum().reset_index(),
            on='day_of_week'
        )
        
        # Monthly aggregation
        bio_monthly = bio_df.groupby('month_year')['total_bio_updates'].sum()
        demo_monthly = demo_df.groupby('month_year')['total_demo_updates'].sum()
        enrol_monthly = enrol_df.groupby('month_year')['total_enrolments'].sum()
        
        return {
            'daily': daily,
            'day_of_week': day_of_week,
            'bio_monthly': bio_monthly,
            'demo_monthly': demo_monthly,
            'enrol_monthly': enrol_monthly
        }
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the dashboard."""
        bio_df, demo_df, enrol_df = self.load_all_data()
        pincode_data = self.get_pincode_analytics()
        state_data = self.get_state_analytics()
        
        return {
            'total_bio_updates': int(bio_df['total_bio_updates'].sum()),
            'total_demo_updates': int(demo_df['total_demo_updates'].sum()),
            'total_enrolments': int(enrol_df['total_enrolments'].sum()),
            'unique_pincodes': int(pincode_data['pincode'].nunique()),
            'unique_states': int(bio_df['state'].nunique()),
            'unique_districts': int(bio_df['district'].nunique()),
            'date_range': {
                'start': bio_df['date'].min().strftime('%Y-%m-%d'),
                'end': bio_df['date'].max().strftime('%Y-%m-%d')
            },
            'avg_ivi': float(pincode_data['identity_velocity_index'].mean()),
            'avg_bsi': float(pincode_data['biometric_stress_index'].mean()),
            'top_state': state_data.nlargest(1, 'total_updates')['state'].iloc[0],
            'high_stress_state': state_data.nlargest(1, 'BSI')['state'].iloc[0]
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
        return _last_load_time.strftime('%Y-%m-%d %H:%M:%S')
    return None


def check_for_new_data(data_dir: str = "data") -> Dict[str, int]:
    """Check if there are new CSV files that haven't been loaded.
    
    Returns:
        Dict with counts of files per data folder.
    """
    data_path = Path(data_dir)
    folders = ['api_data_aadhar_biometric', 'api_data_aadhar_demographic', 'api_data_aadhar_enrolment']
    
    file_counts = {}
    for folder in folders:
        folder_path = data_path / folder
        if folder_path.exists():
            csv_files = list(folder_path.glob("*.csv"))
            file_counts[folder] = len(csv_files)
    
    return file_counts

