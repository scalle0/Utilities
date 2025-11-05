#!/usr/bin/env python3
"""
Electricity Price Fetcher Module
Fetches day-ahead electricity prices from various sources
Supports multiple markets and price providers
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PriceFetcher:
    """Base class for price fetching"""

    def __init__(self, config: Dict):
        self.config = config
        self.currency = config.get('currency', 'EUR')
        self.timezone = config.get('timezone', 'UTC')

    def fetch_prices(self, date: datetime) -> pd.DataFrame:
        """Fetch prices for a specific date"""
        raise NotImplementedError("Subclasses must implement fetch_prices")

    def save_prices(self, prices: pd.DataFrame, filename: str):
        """Save prices to CSV file"""
        prices.to_csv(filename, index=False)
        logger.info(f"Prices saved to {filename}")


class EntsoeAPIFetcher(PriceFetcher):
    """
    Fetches prices from ENTSO-E Transparency Platform
    Covers most European countries
    Free API key required: https://transparency.entsoe.eu/
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('entsoe_api_key')
        self.area_code = config.get('area_code', '10YNL----------L')  # Netherlands default
        self.base_url = 'https://web-api.tp.entsoe.eu/api'

        if not self.api_key:
            raise ValueError("ENTSO-E API key is required")

    def fetch_prices(self, date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Fetch day-ahead prices from ENTSO-E

        Args:
            date: Date to fetch prices for (defaults to tomorrow)

        Returns:
            DataFrame with columns: timestamp, price, unit
        """
        if date is None:
            date = datetime.now() + timedelta(days=1)

        # ENTSO-E uses period start/end in UTC
        period_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)

        params = {
            'securityToken': self.api_key,
            'documentType': 'A44',  # Day-ahead prices
            'in_Domain': self.area_code,
            'out_Domain': self.area_code,
            'periodStart': period_start.strftime('%Y%m%d%H%M'),
            'periodEnd': period_end.strftime('%Y%m%d%H%M')
        }

        try:
            logger.info(f"Fetching ENTSO-E prices for {date.date()}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            # Extract prices
            prices = []
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'}

            for timeseries in root.findall('.//ns:TimeSeries', ns):
                for point in timeseries.findall('.//ns:Point', ns):
                    position = int(point.find('ns:position', ns).text)
                    price = float(point.find('ns:price.amount', ns).text)

                    # Calculate timestamp (position starts at 1)
                    timestamp = period_start + timedelta(hours=position - 1)
                    prices.append({
                        'timestamp': timestamp,
                        'price': price,
                        'unit': 'EUR/MWh'
                    })

            df = pd.DataFrame(prices)
            df = df.sort_values('timestamp').reset_index(drop=True)

            # Convert to price per kWh
            df['price_per_kwh'] = df['price'] / 1000

            logger.info(f"Fetched {len(df)} price points")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ENTSO-E prices: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing ENTSO-E response: {e}")
            raise


class NordPoolFetcher(PriceFetcher):
    """
    Fetches prices from Nord Pool (Scandinavian market)
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.area = config.get('area', 'NO1')  # Norway default
        self.base_url = 'https://www.nordpoolgroup.com/api/marketdata/page/10'

    def fetch_prices(self, date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch day-ahead prices from Nord Pool"""
        if date is None:
            date = datetime.now() + timedelta(days=1)

        try:
            logger.info(f"Fetching Nord Pool prices for {date.date()}")

            params = {
                'currency': self.currency,
                'endDate': date.strftime('%d-%m-%Y')
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Parse the response (structure may vary)
            prices = []
            # Implementation depends on actual API structure
            # This is a placeholder

            logger.warning("Nord Pool fetcher needs API structure verification")
            return pd.DataFrame(prices)

        except Exception as e:
            logger.error(f"Error fetching Nord Pool prices: {e}")
            raise


class TibberAPIFetcher(PriceFetcher):
    """
    Fetches prices from Tibber API (if you're a Tibber customer)
    Tibber provides prices for several European countries
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('tibber_api_key')
        self.base_url = 'https://api.tibber.com/v1-beta/gql'

        if not self.api_key:
            raise ValueError("Tibber API key is required")

    def fetch_prices(self, date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch prices from Tibber API"""
        query = """
        {
          viewer {
            homes {
              currentSubscription {
                priceInfo {
                  today {
                    total
                    energy
                    tax
                    startsAt
                  }
                  tomorrow {
                    total
                    energy
                    tax
                    startsAt
                  }
                }
              }
            }
          }
        }
        """

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            logger.info("Fetching Tibber prices")
            response = requests.post(
                self.base_url,
                json={'query': query},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            prices = []
            homes = data['data']['viewer']['homes']

            if homes:
                price_info = homes[0]['currentSubscription']['priceInfo']

                # Process today's prices
                for price_point in price_info['today']:
                    prices.append({
                        'timestamp': datetime.fromisoformat(price_point['startsAt'].replace('Z', '+00:00')),
                        'price': price_point['total'],
                        'energy_price': price_point['energy'],
                        'tax': price_point['tax'],
                        'unit': self.currency + '/kWh'
                    })

                # Process tomorrow's prices
                for price_point in price_info['tomorrow']:
                    prices.append({
                        'timestamp': datetime.fromisoformat(price_point['startsAt'].replace('Z', '+00:00')),
                        'price': price_point['total'],
                        'energy_price': price_point['energy'],
                        'tax': price_point['tax'],
                        'unit': self.currency + '/kWh'
                    })

            df = pd.DataFrame(prices)
            df = df.sort_values('timestamp').reset_index(drop=True)
            df['price_per_kwh'] = df['price']

            logger.info(f"Fetched {len(df)} price points from Tibber")
            return df

        except Exception as e:
            logger.error(f"Error fetching Tibber prices: {e}")
            raise


class ManualPriceFetcher(PriceFetcher):
    """
    Loads prices from a manually created CSV file
    Useful for testing or if you have prices from another source
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.price_file = config.get('price_file', 'manual_prices.csv')

    def fetch_prices(self, date: Optional[datetime] = None) -> pd.DataFrame:
        """Load prices from CSV file"""
        try:
            logger.info(f"Loading prices from {self.price_file}")
            df = pd.read_csv(self.price_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            if date:
                # Filter for specific date
                df = df[df['timestamp'].dt.date == date.date()]

            logger.info(f"Loaded {len(df)} price points")
            return df

        except Exception as e:
            logger.error(f"Error loading manual prices: {e}")
            raise


def get_price_fetcher(config: Dict) -> PriceFetcher:
    """
    Factory function to get the appropriate price fetcher

    Args:
        config: Configuration dictionary with 'provider' key

    Returns:
        Appropriate PriceFetcher instance
    """
    provider = config.get('provider', 'manual').lower()

    fetchers = {
        'entsoe': EntsoeAPIFetcher,
        'nordpool': NordPoolFetcher,
        'tibber': TibberAPIFetcher,
        'manual': ManualPriceFetcher
    }

    if provider not in fetchers:
        raise ValueError(f"Unknown provider: {provider}. Options: {list(fetchers.keys())}")

    return fetchers[provider](config)


# Example usage
if __name__ == '__main__':
    # Example configuration for ENTSO-E
    config = {
        'provider': 'entsoe',
        'entsoe_api_key': 'YOUR_API_KEY_HERE',
        'area_code': '10YNL----------L',  # Netherlands
        'currency': 'EUR',
        'timezone': 'Europe/Amsterdam'
    }

    try:
        fetcher = get_price_fetcher(config)
        tomorrow = datetime.now() + timedelta(days=1)
        prices = fetcher.fetch_prices(tomorrow)

        print("\nDay-ahead electricity prices:")
        print(prices.head())

        # Save to file
        fetcher.save_prices(prices, 'electricity_prices.csv')

    except Exception as e:
        logger.error(f"Error: {e}")
