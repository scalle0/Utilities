#!/usr/bin/env python3
"""
Battery Automation Main Script
Orchestrates the entire battery optimization and control process
- Fetches electricity prices
- Optimizes charging schedule
- Updates Growatt inverter settings
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Import local modules
from price_fetcher import get_price_fetcher
from battery_optimizer import BatteryOptimizer
from growatt_controller import get_controller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('battery_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BatteryAutomation:
    """Main automation orchestrator"""

    def __init__(self, config_file: str = 'battery_config.json'):
        """
        Initialize automation with configuration

        Args:
            config_file: Path to JSON configuration file
        """
        self.config_file = config_file
        self.config = self.load_config()

        # Initialize components
        self.price_fetcher = None
        self.optimizer = None
        self.controller = None

        self.output_dir = Path(self.config.get('output_dir', 'battery_data'))
        self.output_dir.mkdir(exist_ok=True)

    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_file}")
            logger.info("Please create battery_config.json. See battery_config.example.json")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)

    def initialize_components(self):
        """Initialize all components based on configuration"""
        logger.info("Initializing components...")

        # Initialize price fetcher
        try:
            self.price_fetcher = get_price_fetcher(self.config['price_fetcher'])
            logger.info(f"Price fetcher initialized: {self.config['price_fetcher']['provider']}")
        except Exception as e:
            logger.error(f"Failed to initialize price fetcher: {e}")
            raise

        # Initialize battery optimizer
        try:
            self.optimizer = BatteryOptimizer(self.config['battery'])
            logger.info("Battery optimizer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize optimizer: {e}")
            raise

        # Initialize Growatt controller
        try:
            self.controller = get_controller(self.config['growatt'])
            logger.info(f"Growatt controller initialized: {self.config['growatt']['connection_type']}")
        except Exception as e:
            logger.error(f"Failed to initialize controller: {e}")
            raise

    def fetch_prices(self, date: datetime = None) -> 'pd.DataFrame':
        """
        Fetch electricity prices

        Args:
            date: Date to fetch prices for (default: tomorrow)

        Returns:
            DataFrame with prices
        """
        if date is None:
            date = datetime.now() + timedelta(days=1)

        logger.info(f"Fetching prices for {date.date()}")

        try:
            prices = self.price_fetcher.fetch_prices(date)

            # Save prices to file
            price_file = self.output_dir / f"prices_{date.strftime('%Y%m%d')}.csv"
            self.price_fetcher.save_prices(prices, str(price_file))

            return prices

        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
            raise

    def optimize_schedule(self, prices: 'pd.DataFrame') -> dict:
        """
        Optimize charging schedule based on prices

        Args:
            prices: DataFrame with electricity prices

        Returns:
            Optimized schedule dictionary
        """
        logger.info("Optimizing charging schedule...")

        try:
            # Get expected consumption from config or use default
            expected_consumption = self.config['battery'].get('expected_daily_consumption', 8.0)

            # Calculate optimal schedule
            schedule = self.optimizer.calculate_optimal_charging_schedule(
                prices,
                expected_consumption=expected_consumption
            )

            # Save schedule to file
            schedule_file = self.output_dir / f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.optimizer.export_schedule_to_json(schedule, str(schedule_file))

            return schedule

        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            raise

    def apply_schedule(self, schedule: dict) -> bool:
        """
        Apply optimized schedule to Growatt inverter

        Args:
            schedule: Optimized schedule dictionary

        Returns:
            True if successful
        """
        logger.info("Applying schedule to Growatt inverter...")

        try:
            # Get current battery status
            status = self.controller.get_battery_status()
            logger.info(f"Current battery SOC: {status.get('soc', 'unknown')}%")

            # Convert schedule to Growatt time slots
            time_slots = self.optimizer.create_growatt_time_slots(schedule)

            # Apply charging schedule
            success = self.controller.set_charging_schedule(time_slots)

            if success:
                logger.info("✓ Charging schedule applied successfully")
            else:
                logger.error("✗ Failed to apply charging schedule")
                return False

            # Optionally set battery mode for discharge periods
            # This depends on your specific needs and inverter capabilities
            if self.config['growatt'].get('auto_set_modes', False):
                # Set to battery-first mode during expensive hours
                # This is a simplified approach - you may want more sophisticated control
                logger.info("Auto mode switching enabled")

            return True

        except Exception as e:
            logger.error(f"Error applying schedule: {e}")
            return False

    def run_daily_optimization(self):
        """
        Run the complete daily optimization process
        This is the main function called by the scheduler
        """
        logger.info("="*70)
        logger.info("STARTING DAILY BATTERY OPTIMIZATION")
        logger.info("="*70)
        logger.info(f"Timestamp: {datetime.now()}")

        try:
            # Initialize components
            self.initialize_components()

            # Fetch tomorrow's prices
            tomorrow = datetime.now() + timedelta(days=1)
            prices = self.fetch_prices(tomorrow)

            if prices is None or prices.empty:
                logger.error("No price data available")
                return False

            # Optimize schedule
            schedule = self.optimize_schedule(prices)

            # Apply schedule to inverter
            success = self.apply_schedule(schedule)

            if success:
                logger.info("="*70)
                logger.info("✓ DAILY OPTIMIZATION COMPLETED SUCCESSFULLY")
                logger.info("="*70)

                # Save success marker
                marker_file = self.output_dir / f"success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                marker_file.write_text(f"Optimization completed at {datetime.now()}\n")

                return True
            else:
                logger.error("="*70)
                logger.error("✗ DAILY OPTIMIZATION FAILED")
                logger.error("="*70)
                return False

        except Exception as e:
            logger.error(f"Unexpected error during optimization: {e}", exc_info=True)
            return False

    def test_connection(self):
        """
        Test connection to all services
        Useful for debugging
        """
        logger.info("="*70)
        logger.info("TESTING CONNECTIONS")
        logger.info("="*70)

        results = {
            'price_fetcher': False,
            'growatt_controller': False
        }

        # Test price fetcher
        try:
            logger.info("\n1. Testing price fetcher...")
            self.price_fetcher = get_price_fetcher(self.config['price_fetcher'])
            # Try to fetch prices for today
            prices = self.price_fetcher.fetch_prices(datetime.now())
            if prices is not None and not prices.empty:
                logger.info(f"✓ Price fetcher working: {len(prices)} price points retrieved")
                results['price_fetcher'] = True
            else:
                logger.warning("✗ Price fetcher returned no data")
        except Exception as e:
            logger.error(f"✗ Price fetcher error: {e}")

        # Test Growatt controller
        try:
            logger.info("\n2. Testing Growatt controller...")
            self.controller = get_controller(self.config['growatt'])
            status = self.controller.get_battery_status()
            logger.info(f"✓ Growatt controller working: Battery SOC = {status.get('soc', 'unknown')}%")
            results['growatt_controller'] = True
        except Exception as e:
            logger.error(f"✗ Growatt controller error: {e}")

        # Summary
        logger.info("\n" + "="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)
        for component, status in results.items():
            status_icon = "✓" if status else "✗"
            logger.info(f"{status_icon} {component}: {'OK' if status else 'FAILED'}")

        all_ok = all(results.values())
        if all_ok:
            logger.info("\n✓ All systems operational!")
        else:
            logger.warning("\n✗ Some systems failed. Check configuration.")

        return all_ok

    def generate_report(self, days: int = 7):
        """
        Generate a report of battery performance and savings

        Args:
            days: Number of days to include in report
        """
        logger.info(f"Generating {days}-day performance report...")

        # Look for schedule files in output directory
        schedule_files = sorted(self.output_dir.glob("schedule_*.json"))

        if not schedule_files:
            logger.warning("No schedule files found")
            return

        total_savings = 0
        report_data = []

        for schedule_file in schedule_files[-days:]:
            try:
                with open(schedule_file, 'r') as f:
                    schedule = json.load(f)

                savings = schedule.get('expected_savings', {})
                date = schedule.get('generated_at', 'unknown')

                report_data.append({
                    'date': date,
                    'net_savings': savings.get('net_savings', 0),
                    'charging_energy': savings.get('charging_energy_kwh', 0)
                })

                total_savings += savings.get('net_savings', 0)

            except Exception as e:
                logger.error(f"Error reading {schedule_file}: {e}")

        # Print report
        logger.info("\n" + "="*70)
        logger.info(f"BATTERY PERFORMANCE REPORT ({days} days)")
        logger.info("="*70)

        for entry in report_data:
            logger.info(f"{entry['date'][:10]}: "
                       f"Charged {entry['charging_energy']:.1f} kWh, "
                       f"Saved {entry['net_savings']:.2f} €")

        logger.info("-"*70)
        logger.info(f"Total savings: {total_savings:.2f} €")
        logger.info(f"Average per day: {total_savings/len(report_data):.2f} €")
        logger.info(f"Projected monthly: {total_savings/len(report_data)*30:.2f} €")
        logger.info("="*70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Battery Automation - Optimize Growatt battery charging based on electricity prices'
    )

    parser.add_argument(
        'command',
        choices=['run', 'test', 'report'],
        help='Command to execute: run (daily optimization), test (test connections), report (generate report)'
    )

    parser.add_argument(
        '--config',
        default='battery_config.json',
        help='Path to configuration file (default: battery_config.json)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days for report (default: 7)'
    )

    args = parser.parse_args()

    # Create automation instance
    automation = BatteryAutomation(config_file=args.config)

    # Execute command
    if args.command == 'run':
        success = automation.run_daily_optimization()
        sys.exit(0 if success else 1)

    elif args.command == 'test':
        success = automation.test_connection()
        sys.exit(0 if success else 1)

    elif args.command == 'report':
        automation.generate_report(days=args.days)
        sys.exit(0)


if __name__ == '__main__':
    main()
