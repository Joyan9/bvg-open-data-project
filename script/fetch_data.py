import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

import requests
import boto3
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bvg_data_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration Management
class Config:
    """Centralized configuration management for the BVG data fetcher."""
    # S3 Configuration
    S3_BUCKET: str = "bvg-open-data"
    S3_REGION: str = "eu-central-1"

    # BVG API Configuration
    BASE_API_URL: str = 'https://v6.bvg.transport.rest'
    DEFAULT_DURATION: int = 30
    DEFAULT_MAX_RESULTS: int = 50

    # Data Filtering
    INTERESTED_DIRECTIONS: List[str] = [
        "Wedding, Virchow-Klinikum", 
        "S Warschauer Straße"
    ]

    # Stations Configuration
    STATIONS: List[Tuple[str, str]] = [
        ('900110007', 'schoenhauser_alle_bornholmer_strasse'),
        ('900140011', 'antonplatz')
    ]

class BVGDataFetcher:
    """Comprehensive data fetcher for BVG transportation data."""

    def __init__(self, config: Config = Config()):
        """
        Initialize the data fetcher with configuration and AWS clients.
        
        :param config: Configuration object with fetch parameters
        """
        self.config = config
        self.s3_client = boto3.client('s3', region_name=config.S3_REGION)
        
    def fetch_data(
        self, 
        station_id: str, 
        endpoint: str, 
        duration: int = None, 
        max_results: int = None
    ) -> Optional[Dict]:
        """
        Fetch transportation data from BVG REST API.
        
        :param station_id: Unique station identifier
        :param endpoint: 'departures' or 'arrivals'
        :param duration: Time range for results in minutes
        :param max_results: Maximum number of results to fetch
        :return: Parsed JSON response or None
        """
        duration = duration or self.config.DEFAULT_DURATION
        max_results = max_results or self.config.DEFAULT_MAX_RESULTS
        
        url = f"{self.config.BASE_API_URL}/stops/{station_id}/{endpoint}"
        
        try:
            response = requests.get(
                url,
                params={
                    'duration': duration,
                    'results': max_results,
                    'remarks': True
                },
                timeout=10  # Add request timeout
            )
            response.raise_for_status()  # Raise exception for bad status codes
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"API Request Error: {e}")
            return None

    def process_data(
        self, 
        data: Dict, 
        station_id: str, 
        endpoint: str
    ) -> pd.DataFrame:
        """
        Process raw API data into a structured DataFrame.
        
        :param data: Raw API response
        :param station_id: Station identifier
        :param endpoint: 'departures' or 'arrivals'
        :return: Processed DataFrame
        """
        if not data or endpoint not in data:
            logger.warning(f"No data for {endpoint} at station {station_id}")
            return pd.DataFrame()

        processed_data = []
        for item in data.get(endpoint, []):
            # Skip items not matching interested directions
            if (endpoint == 'departures' and 
                item.get('direction', '') not in self.config.INTERESTED_DIRECTIONS):
                continue

            try:
                processed_item = self._extract_item_details(item, station_id, endpoint)
                processed_data.append(processed_item)
            except Exception as e:
                logger.warning(f"Error processing item: {e}")

        return pd.DataFrame(processed_data)

    def _extract_item_details(
        self, 
        item: Dict, 
        station_id: str, 
        endpoint: str
    ) -> Dict:
        """
        Extract detailed information from a single API item.
        
        :param item: Single item from API response
        :param station_id: Station identifier
        :param endpoint: 'departures' or 'arrivals'
        :return: Processed item dictionary
        """
        scheduled_time = item.get('plannedWhen')
        actual_time = item.get('when')

        delay_calc = None
        if scheduled_time and actual_time:
            delay_calc = (
                datetime.fromisoformat(actual_time) - 
                datetime.fromisoformat(scheduled_time)
            ).total_seconds()

        return {
            'trip_id': item.get('tripId'),
            'line_name': item['line']['name'],
            'product': item['line']['product'],
            'station_id': station_id,
            'station_name': item['stop']['name'],
            'direction': item.get('direction', ''),
            'scheduled_time': scheduled_time,
            'actual_time': actual_time,
            'delay': item.get('delay'),
            'delay_calc': delay_calc,
            'occupancy': item.get('occupancy', ''),
            'remarks': json.dumps([
                remark.get('text') for remark in item.get('remarks', [])
            ])
        }

    def save_to_s3(
        self, 
        df: pd.DataFrame, 
        station_name: str, 
        endpoint: str
    ) -> None:
        """
        Save processed DataFrame to S3 as Parquet file.
        
        :param df: DataFrame to save
        :param station_name: Name of the station
        :param endpoint: 'departures' or 'arrivals'
        """
        if df.empty:
            logger.warning(f"No data to save for {station_name} - {endpoint}")
            return

        # Create temporary directory
        temp_dir = os.path.join(os.getcwd(), 'tmp', endpoint)
        os.makedirs(temp_dir, exist_ok=True)

        # Generate filename with timestamp
        filename = (
            f"{station_name}_{endpoint}_"
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"
        )
        local_path = os.path.join(temp_dir, filename)
        s3_key = f"{endpoint}/{filename}"

        try:
            # Save locally and upload to S3
            df.to_parquet(local_path, index=False)
            self.s3_client.upload_file(local_path, self.config.S3_BUCKET, s3_key)
            
            logger.info(f"Uploaded {s3_key} to {self.config.S3_BUCKET}")
            os.remove(local_path)  # Clean up local file
        
        except Exception as e:
            logger.error(f"S3 Upload Error: {e}")

    def fetch_process_save(self) -> None:
        """
        Orchestrate data fetching, processing, and saving for all stations.
        """
        for station_id, station_name in self.config.STATIONS:
            for endpoint in ['departures', 'arrivals']:
                try:
                    # Fetch data
                    data = self.fetch_data(station_id, endpoint)
                    if not data:
                        continue

                    # Process data
                    df = self.process_data(data, station_id, endpoint)
                    
                    # Save to S3
                    self.save_to_s3(df, station_name, endpoint)
                
                except Exception as e:
                    logger.error(f"Error processing {station_name} - {endpoint}: {e}")

def main():
    """Main execution function."""
    try:
        fetcher = BVGDataFetcher()
        fetcher.fetch_process_save()
    except Exception as e:
        logger.critical(f"Unhandled error in main execution: {e}")

if __name__ == "__main__":
    main()
