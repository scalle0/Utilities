#!/usr/bin/env python3
"""
ESP32 Bridge Module
Sends optimized charging schedules to ESP32 controller via HTTP API
"""

import requests
import json
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ESP32Bridge:
    """
    Bridge between Python optimizer and ESP32 controller
    """

    def __init__(self, config: Dict):
        """
        Initialize ESP32 bridge

        Args:
            config: Dictionary containing:
                - esp32_ip: IP address of ESP32
                - esp32_port: Port (default 80)
                - timeout: Request timeout in seconds
        """
        self.esp32_ip = config.get('esp32_ip', '192.168.1.50')
        self.esp32_port = config.get('esp32_port', 80)
        self.timeout = config.get('timeout', 10)
        self.base_url = f"http://{self.esp32_ip}:{self.esp32_port}"

        logger.info(f"ESP32 Bridge initialized: {self.base_url}")

    def test_connection(self) -> bool:
        """
        Test connection to ESP32

        Returns:
            True if ESP32 is reachable
        """
        try:
            logger.info("Testing connection to ESP32...")
            response = requests.get(
                f"{self.base_url}/api/status",
                timeout=self.timeout
            )

            if response.status_code == 200:
                status = response.json()
                logger.info(f"✓ ESP32 connected - Battery SOC: {status.get('soc', 'unknown')}%")
                return True
            else:
                logger.error(f"✗ ESP32 returned status code: {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            logger.error(f"✗ Cannot connect to ESP32 at {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"✗ Connection to ESP32 timed out")
            return False
        except Exception as e:
            logger.error(f"✗ Error connecting to ESP32: {e}")
            return False

    def get_battery_status(self) -> Dict:
        """
        Get current battery status from ESP32

        Returns:
            Dictionary with battery status
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/status",
                timeout=self.timeout
            )
            response.raise_for_status()

            status = response.json()
            logger.info(f"Battery status: SOC={status.get('soc')}%, "
                       f"Power={status.get('power')}W")
            return status

        except Exception as e:
            logger.error(f"Error getting battery status: {e}")
            return {}

    def get_current_schedule(self) -> Dict:
        """
        Get current schedule from ESP32

        Returns:
            Dictionary with current schedule
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/schedule",
                timeout=self.timeout
            )
            response.raise_for_status()

            schedule = response.json()
            logger.info(f"Current schedule has {schedule.get('num_slots', 0)} time slots")
            return schedule

        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return {}

    def send_schedule(self, schedule: Dict) -> bool:
        """
        Send optimized schedule to ESP32

        Args:
            schedule: Optimized schedule from BatteryOptimizer

        Returns:
            True if successful
        """
        try:
            logger.info("Sending schedule to ESP32...")

            # Convert Python schedule to ESP32 format
            esp32_schedule = self._convert_schedule(schedule)

            # Send to ESP32
            response = requests.post(
                f"{self.base_url}/api/schedule",
                json=esp32_schedule,
                timeout=self.timeout
            )
            response.raise_for_status()

            logger.info("✓ Schedule sent to ESP32 successfully")
            logger.info("ESP32 will now apply schedule to Growatt inverter")

            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error sending schedule to ESP32: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return False

    def _convert_schedule(self, schedule: Dict) -> Dict:
        """
        Convert optimizer schedule format to ESP32 format

        Args:
            schedule: Schedule from BatteryOptimizer

        Returns:
            Schedule in ESP32 format
        """
        charging_windows = []

        for window in schedule.get('charging_windows', []):
            start_time = window['start']
            end_time = window['end']

            charging_windows.append({
                'enabled': True,
                'start_hour': start_time.hour,
                'start_minute': start_time.minute,
                'end_hour': end_time.hour,
                'end_minute': end_time.minute,
                'power_percent': 100
            })

        return {
            'charging_windows': charging_windows,
            'timestamp': datetime.now().isoformat()
        }

    def reboot_esp32(self) -> bool:
        """
        Reboot ESP32 (if endpoint is implemented)

        Returns:
            True if successful
        """
        try:
            logger.info("Rebooting ESP32...")
            response = requests.post(
                f"{self.base_url}/api/reboot",
                timeout=5
            )
            return response.status_code == 200
        except:
            logger.warning("Reboot endpoint not available or failed")
            return False


# Integration with battery_automation.py
def apply_schedule_via_esp32(schedule: Dict, config: Dict) -> bool:
    """
    Helper function to apply schedule via ESP32

    Args:
        schedule: Optimized schedule
        config: ESP32 configuration

    Returns:
        True if successful
    """
    bridge = ESP32Bridge(config)

    # Test connection first
    if not bridge.test_connection():
        logger.error("Cannot connect to ESP32")
        return False

    # Send schedule
    success = bridge.send_schedule(schedule)

    if success:
        # Verify schedule was applied
        current_schedule = bridge.get_current_schedule()
        num_slots = current_schedule.get('num_slots', 0)
        expected_slots = len(schedule.get('charging_windows', []))

        if num_slots == expected_slots:
            logger.info(f"✓ Schedule verified: {num_slots} time slots active")
        else:
            logger.warning(f"⚠ Schedule mismatch: expected {expected_slots}, got {num_slots}")

    return success


# Example usage and testing
if __name__ == '__main__':
    # Example configuration
    config = {
        'esp32_ip': '192.168.1.50',
        'esp32_port': 80,
        'timeout': 10
    }

    # Create bridge
    bridge = ESP32Bridge(config)

    # Test connection
    if bridge.test_connection():
        print("✓ Connection test passed")

        # Get battery status
        status = bridge.get_battery_status()
        print(f"Battery SOC: {status.get('soc')}%")

        # Get current schedule
        schedule = bridge.get_current_schedule()
        print(f"Active time slots: {schedule.get('num_slots')}")

        # Example: Send test schedule
        test_schedule = {
            'charging_windows': [
                {
                    'start': datetime.strptime('2025-11-06 02:00', '%Y-%m-%d %H:%M'),
                    'end': datetime.strptime('2025-11-06 06:00', '%Y-%m-%d %H:%M'),
                    'energy_kwh': 8.0,
                    'price': 0.10
                }
            ]
        }

        # Uncomment to test sending schedule
        # bridge.send_schedule(test_schedule)

    else:
        print("✗ Connection test failed")
        print("Check that:")
        print(f"  1. ESP32 is powered on")
        print(f"  2. ESP32 is connected to WiFi")
        print(f"  3. IP address is correct: {config['esp32_ip']}")
        print(f"  4. You can ping the ESP32")
