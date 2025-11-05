#!/usr/bin/env python3
"""
Battery Charging Optimizer
Optimizes battery charging schedule based on electricity prices
Determines optimal charging windows and battery usage patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatteryOptimizer:
    """
    Optimizes battery charging schedule based on electricity prices
    """

    def __init__(self, config: Dict):
        """
        Initialize optimizer with battery and system parameters

        Args:
            config: Dictionary containing:
                - battery_capacity_kwh: Total battery capacity in kWh
                - max_charge_rate_kw: Maximum charging rate in kW
                - max_discharge_rate_kw: Maximum discharge rate in kW
                - min_soc: Minimum state of charge (0-100)
                - max_soc: Maximum state of charge (0-100)
                - efficiency: Round-trip efficiency (0-1)
                - reserve_capacity: Reserve capacity to maintain (kWh)
        """
        self.battery_capacity = config.get('battery_capacity_kwh', 10.0)
        self.max_charge_rate = config.get('max_charge_rate_kw', 5.0)
        self.max_discharge_rate = config.get('max_discharge_rate_kw', 5.0)
        self.min_soc = config.get('min_soc', 10.0)
        self.max_soc = config.get('max_soc', 95.0)
        self.efficiency = config.get('efficiency', 0.95)
        self.reserve_capacity = config.get('reserve_capacity_kwh', 1.0)

        # Derived values
        self.usable_capacity = self.battery_capacity * (self.max_soc - self.min_soc) / 100
        self.min_capacity = self.battery_capacity * self.min_soc / 100

        logger.info(f"Battery Optimizer initialized:")
        logger.info(f"  Capacity: {self.battery_capacity} kWh")
        logger.info(f"  Usable capacity: {self.usable_capacity:.2f} kWh")
        logger.info(f"  Charge rate: {self.max_charge_rate} kW")
        logger.info(f"  Efficiency: {self.efficiency * 100}%")

    def analyze_prices(self, prices_df: pd.DataFrame) -> Dict:
        """
        Analyze price data to identify patterns

        Args:
            prices_df: DataFrame with 'timestamp' and 'price_per_kwh' columns

        Returns:
            Dictionary with price analysis
        """
        if prices_df.empty:
            raise ValueError("Price data is empty")

        analysis = {
            'min_price': prices_df['price_per_kwh'].min(),
            'max_price': prices_df['price_per_kwh'].max(),
            'avg_price': prices_df['price_per_kwh'].mean(),
            'median_price': prices_df['price_per_kwh'].median(),
            'std_price': prices_df['price_per_kwh'].std()
        }

        # Find price percentiles
        analysis['price_10th'] = prices_df['price_per_kwh'].quantile(0.10)
        analysis['price_25th'] = prices_df['price_per_kwh'].quantile(0.25)
        analysis['price_75th'] = prices_df['price_per_kwh'].quantile(0.75)
        analysis['price_90th'] = prices_df['price_per_kwh'].quantile(0.90)

        # Find cheapest and most expensive hours
        sorted_prices = prices_df.sort_values('price_per_kwh')
        analysis['cheapest_hours'] = sorted_prices.head(6)['timestamp'].tolist()
        analysis['expensive_hours'] = sorted_prices.tail(6)['timestamp'].tolist()

        logger.info(f"Price Analysis:")
        logger.info(f"  Range: {analysis['min_price']:.4f} - {analysis['max_price']:.4f} €/kWh")
        logger.info(f"  Average: {analysis['avg_price']:.4f} €/kWh")
        logger.info(f"  Potential savings: {(analysis['max_price'] - analysis['min_price']) * self.battery_capacity:.2f} €/day")

        return analysis

    def calculate_optimal_charging_schedule(
        self,
        prices_df: pd.DataFrame,
        expected_consumption: float = 8.0,
        solar_production: pd.DataFrame = None
    ) -> Dict:
        """
        Calculate optimal charging schedule

        Args:
            prices_df: DataFrame with 'timestamp' and 'price_per_kwh'
            expected_consumption: Expected daily consumption in kWh
            solar_production: Optional DataFrame with solar production forecast

        Returns:
            Dictionary with optimal schedule
        """
        logger.info("Calculating optimal charging schedule...")

        # Analyze prices
        analysis = self.analyze_prices(prices_df)

        # Determine charging threshold (charge when price below this)
        # Use 25th percentile as default threshold
        charge_threshold = analysis['price_25th']

        # Determine discharge threshold (use battery when price above this)
        # Use 75th percentile as default threshold
        discharge_threshold = analysis['price_75th']

        # Find optimal charging windows
        charging_windows = self._find_charging_windows(
            prices_df,
            charge_threshold,
            expected_consumption
        )

        # Find optimal discharge windows
        discharge_windows = self._find_discharge_windows(
            prices_df,
            discharge_threshold
        )

        # Calculate expected savings
        savings = self._calculate_savings(
            prices_df,
            charging_windows,
            discharge_windows
        )

        schedule = {
            'charge_threshold': charge_threshold,
            'discharge_threshold': discharge_threshold,
            'charging_windows': charging_windows,
            'discharge_windows': discharge_windows,
            'expected_savings': savings,
            'price_analysis': analysis
        }

        self._log_schedule(schedule)

        return schedule

    def _find_charging_windows(
        self,
        prices_df: pd.DataFrame,
        threshold: float,
        expected_consumption: float
    ) -> List[Dict]:
        """
        Find optimal charging time windows

        Args:
            prices_df: Price data
            threshold: Price threshold for charging
            expected_consumption: Expected consumption to cover

        Returns:
            List of charging windows with start, end, and energy
        """
        # Find all hours below threshold
        cheap_hours = prices_df[prices_df['price_per_kwh'] <= threshold].copy()

        if cheap_hours.empty:
            logger.warning("No hours below charging threshold, using cheapest hours")
            cheap_hours = prices_df.nsmallest(6, 'price_per_kwh')

        # Sort by price (cheapest first)
        cheap_hours = cheap_hours.sort_values('price_per_kwh')

        # Calculate energy needed
        energy_needed = min(expected_consumption, self.usable_capacity)

        # Select hours to charge (considering charge rate)
        hours_needed = int(np.ceil(energy_needed / self.max_charge_rate))
        selected_hours = cheap_hours.head(hours_needed)

        # Group consecutive hours into windows
        selected_hours = selected_hours.sort_values('timestamp')
        windows = []
        current_window = None

        for _, row in selected_hours.iterrows():
            timestamp = row['timestamp']
            price = row['price_per_kwh']

            if current_window is None:
                # Start new window
                current_window = {
                    'start': timestamp,
                    'end': timestamp + timedelta(hours=1),
                    'price': price,
                    'energy_kwh': min(self.max_charge_rate, energy_needed)
                }
            elif (timestamp - current_window['end']).total_seconds() <= 3600:
                # Extend current window
                current_window['end'] = timestamp + timedelta(hours=1)
                current_window['energy_kwh'] += min(self.max_charge_rate, energy_needed)
            else:
                # Save current window and start new one
                windows.append(current_window)
                current_window = {
                    'start': timestamp,
                    'end': timestamp + timedelta(hours=1),
                    'price': price,
                    'energy_kwh': min(self.max_charge_rate, energy_needed)
                }

        if current_window:
            windows.append(current_window)

        # Limit total energy to battery capacity
        total_energy = 0
        for window in windows:
            available_capacity = self.usable_capacity - total_energy
            window['energy_kwh'] = min(window['energy_kwh'], available_capacity)
            total_energy += window['energy_kwh']

        return windows

    def _find_discharge_windows(
        self,
        prices_df: pd.DataFrame,
        threshold: float
    ) -> List[Dict]:
        """
        Find optimal discharge time windows

        Args:
            prices_df: Price data
            threshold: Price threshold for discharging

        Returns:
            List of discharge windows
        """
        # Find all hours above threshold
        expensive_hours = prices_df[prices_df['price_per_kwh'] >= threshold].copy()

        if expensive_hours.empty:
            logger.warning("No hours above discharge threshold")
            return []

        # Sort by price (most expensive first)
        expensive_hours = expensive_hours.sort_values('price_per_kwh', ascending=False)

        # Group consecutive hours
        expensive_hours = expensive_hours.sort_values('timestamp')
        windows = []
        current_window = None

        for _, row in expensive_hours.iterrows():
            timestamp = row['timestamp']
            price = row['price_per_kwh']

            if current_window is None:
                current_window = {
                    'start': timestamp,
                    'end': timestamp + timedelta(hours=1),
                    'price': price,
                    'mode': 'battery_first'
                }
            elif (timestamp - current_window['end']).total_seconds() <= 3600:
                current_window['end'] = timestamp + timedelta(hours=1)
            else:
                windows.append(current_window)
                current_window = {
                    'start': timestamp,
                    'end': timestamp + timedelta(hours=1),
                    'price': price,
                    'mode': 'battery_first'
                }

        if current_window:
            windows.append(current_window)

        return windows

    def _calculate_savings(
        self,
        prices_df: pd.DataFrame,
        charging_windows: List[Dict],
        discharge_windows: List[Dict]
    ) -> Dict:
        """
        Calculate expected cost savings

        Args:
            prices_df: Price data
            charging_windows: Charging schedule
            discharge_windows: Discharge schedule

        Returns:
            Dictionary with savings calculation
        """
        # Calculate charging cost
        charging_cost = 0
        charging_energy = 0
        for window in charging_windows:
            energy = window['energy_kwh']
            # Get average price during window
            window_prices = prices_df[
                (prices_df['timestamp'] >= window['start']) &
                (prices_df['timestamp'] < window['end'])
            ]
            avg_price = window_prices['price_per_kwh'].mean()
            charging_cost += energy * avg_price
            charging_energy += energy

        # Calculate discharge value (energy used from battery during expensive hours)
        discharge_value = 0
        discharge_energy = min(charging_energy * self.efficiency, self.usable_capacity)

        for window in discharge_windows:
            window_prices = prices_df[
                (prices_df['timestamp'] >= window['start']) &
                (prices_df['timestamp'] < window['end'])
            ]
            avg_price = window_prices['price_per_kwh'].mean()

            # Assume we can discharge at max rate during this window
            hours = (window['end'] - window['start']).total_seconds() / 3600
            energy_this_window = min(
                self.max_discharge_rate * hours,
                discharge_energy
            )
            discharge_value += energy_this_window * avg_price
            discharge_energy -= energy_this_window

            if discharge_energy <= 0:
                break

        # Calculate net savings
        net_savings = discharge_value - charging_cost
        efficiency_loss = charging_energy * (1 - self.efficiency) * prices_df['price_per_kwh'].mean()

        return {
            'charging_cost': charging_cost,
            'charging_energy_kwh': charging_energy,
            'discharge_value': discharge_value,
            'efficiency_loss_cost': efficiency_loss,
            'net_savings': net_savings,
            'savings_percentage': (net_savings / discharge_value * 100) if discharge_value > 0 else 0
        }

    def _log_schedule(self, schedule: Dict):
        """Log the optimized schedule"""
        logger.info("\n" + "="*60)
        logger.info("OPTIMAL BATTERY SCHEDULE")
        logger.info("="*60)

        logger.info(f"\nPrice Thresholds:")
        logger.info(f"  Charge when below: {schedule['charge_threshold']:.4f} €/kWh")
        logger.info(f"  Use battery when above: {schedule['discharge_threshold']:.4f} €/kWh")

        logger.info(f"\nCharging Windows ({len(schedule['charging_windows'])}):")
        for i, window in enumerate(schedule['charging_windows'], 1):
            logger.info(f"  {i}. {window['start'].strftime('%H:%M')}-{window['end'].strftime('%H:%M')}: "
                       f"{window['energy_kwh']:.1f} kWh @ {window['price']:.4f} €/kWh")

        logger.info(f"\nDischarge Windows ({len(schedule['discharge_windows'])}):")
        for i, window in enumerate(schedule['discharge_windows'], 1):
            logger.info(f"  {i}. {window['start'].strftime('%H:%M')}-{window['end'].strftime('%H:%M')}: "
                       f"Battery First mode @ {window['price']:.4f} €/kWh")

        savings = schedule['expected_savings']
        logger.info(f"\nExpected Savings:")
        logger.info(f"  Charging cost: {savings['charging_cost']:.2f} €")
        logger.info(f"  Discharge value: {savings['discharge_value']:.2f} €")
        logger.info(f"  Net savings: {savings['net_savings']:.2f} €/day")
        logger.info(f"  Monthly potential: {savings['net_savings'] * 30:.2f} €")
        logger.info("="*60 + "\n")

    def export_schedule_to_json(self, schedule: Dict, filename: str):
        """
        Export schedule to JSON file for use by control systems

        Args:
            schedule: Optimized schedule
            filename: Output JSON filename
        """
        import json

        # Convert datetime objects to strings
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'charge_threshold': schedule['charge_threshold'],
            'discharge_threshold': schedule['discharge_threshold'],
            'charging_windows': [
                {
                    'start': w['start'].isoformat(),
                    'end': w['end'].isoformat(),
                    'energy_kwh': w['energy_kwh'],
                    'price': w['price']
                }
                for w in schedule['charging_windows']
            ],
            'discharge_windows': [
                {
                    'start': w['start'].isoformat(),
                    'end': w['end'].isoformat(),
                    'mode': w['mode'],
                    'price': w['price']
                }
                for w in schedule['discharge_windows']
            ],
            'expected_savings': schedule['expected_savings']
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Schedule exported to {filename}")

    def create_growatt_time_slots(self, schedule: Dict) -> List[Dict]:
        """
        Convert optimized schedule to Growatt time slot format

        Growatt supports multiple time slots for AC charging control
        Format: {start_time, end_time, enabled, power_percentage}

        Args:
            schedule: Optimized schedule

        Returns:
            List of time slots in Growatt format
        """
        time_slots = []

        for i, window in enumerate(schedule['charging_windows']):
            slot = {
                'slot_number': i + 1,
                'enabled': True,
                'start_hour': window['start'].hour,
                'start_minute': window['start'].minute,
                'end_hour': window['end'].hour,
                'end_minute': window['end'].minute,
                'power_percentage': 100,  # Charge at full power
                'mode': 'charge'
            }
            time_slots.append(slot)

        logger.info(f"Created {len(time_slots)} Growatt time slots")
        return time_slots


# Example usage
if __name__ == '__main__':
    # Battery configuration
    config = {
        'battery_capacity_kwh': 10.0,
        'max_charge_rate_kw': 5.0,
        'max_discharge_rate_kw': 5.0,
        'min_soc': 10.0,
        'max_soc': 95.0,
        'efficiency': 0.95,
        'reserve_capacity_kwh': 1.0
    }

    # Initialize optimizer
    optimizer = BatteryOptimizer(config)

    # Load sample prices (you would get this from price_fetcher.py)
    sample_prices = pd.DataFrame({
        'timestamp': pd.date_range('2025-11-06', periods=24, freq='H'),
        'price_per_kwh': [0.15, 0.14, 0.13, 0.12, 0.11, 0.12, 0.16, 0.20,
                          0.25, 0.23, 0.20, 0.18, 0.17, 0.16, 0.17, 0.19,
                          0.22, 0.28, 0.30, 0.27, 0.23, 0.20, 0.18, 0.16]
    })

    # Calculate optimal schedule
    schedule = optimizer.calculate_optimal_charging_schedule(
        sample_prices,
        expected_consumption=8.0
    )

    # Export schedule
    optimizer.export_schedule_to_json(schedule, 'battery_schedule.json')

    # Create Growatt time slots
    time_slots = optimizer.create_growatt_time_slots(schedule)
    print("\nGrowatt Time Slots:")
    for slot in time_slots:
        print(f"  Slot {slot['slot_number']}: {slot['start_hour']:02d}:{slot['start_minute']:02d} - "
              f"{slot['end_hour']:02d}:{slot['end_minute']:02d}")
