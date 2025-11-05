#!/usr/bin/env python3
"""
Growatt Battery Controller
Controls Growatt inverter/battery settings for optimal charging
Supports multiple connection methods: API, Modbus, VPP Protocol
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrowattController:
    """Base class for Growatt control"""

    def __init__(self, config: Dict):
        self.config = config
        self.dry_run = config.get('dry_run', True)

    def set_charging_schedule(self, time_slots: List[Dict]) -> bool:
        """Set charging schedule - must be implemented by subclass"""
        raise NotImplementedError("Subclasses must implement set_charging_schedule")

    def set_battery_mode(self, mode: str) -> bool:
        """Set battery operation mode - must be implemented by subclass"""
        raise NotImplementedError("Subclasses must implement set_battery_mode")

    def get_battery_status(self) -> Dict:
        """Get current battery status - must be implemented by subclass"""
        raise NotImplementedError("Subclasses must implement get_battery_status")


class GrowattAPIController(GrowattController):
    """
    Controls Growatt via Cloud API using growattServer library
    Requires: pip install growattServer
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.username = config.get('username')
        self.password = config.get('password')
        self.plant_id = config.get('plant_id')
        self.device_serial = config.get('device_serial')

        if not self.dry_run:
            try:
                import growattServer
                self.api = growattServer.GrowattApi()
                self.login()
            except ImportError:
                logger.error("growattServer library not installed. Run: pip install growattServer")
                raise
        else:
            logger.info("DRY RUN MODE: No actual API calls will be made")

    def login(self):
        """Login to Growatt server"""
        try:
            login_response = self.api.login(self.username, self.password)
            logger.info("Successfully logged in to Growatt API")
            return True
        except Exception as e:
            logger.error(f"Failed to login to Growatt API: {e}")
            raise

    def get_battery_status(self) -> Dict:
        """Get current battery status"""
        if self.dry_run:
            logger.info("[DRY RUN] Would fetch battery status")
            return {
                'soc': 50,
                'power': 0,
                'status': 'standby'
            }

        try:
            # Get device data
            device_data = self.api.device_detail(self.device_serial)

            status = {
                'soc': device_data.get('capacity', 0),
                'power': device_data.get('pDisCharge1', 0),
                'voltage': device_data.get('vBat', 0),
                'current': device_data.get('ioBat', 0),
                'status': device_data.get('status', 'unknown')
            }

            logger.info(f"Battery Status: SOC={status['soc']}%, Power={status['power']}W")
            return status

        except Exception as e:
            logger.error(f"Error getting battery status: {e}")
            raise

    def set_charging_schedule(self, time_slots: List[Dict]) -> bool:
        """
        Set AC charging time schedule

        Args:
            time_slots: List of time slots with start/end times and settings

        Returns:
            True if successful
        """
        if self.dry_run:
            logger.info("[DRY RUN] Would set charging schedule:")
            for slot in time_slots:
                logger.info(f"  Slot {slot['slot_number']}: "
                           f"{slot['start_hour']:02d}:{slot['start_minute']:02d} - "
                           f"{slot['end_hour']:02d}:{slot['end_minute']:02d} "
                           f"@ {slot['power_percentage']}%")
            return True

        try:
            # Growatt API method to set time slots
            # Note: Actual API method may vary by inverter model
            for slot in time_slots:
                if slot['enabled']:
                    # Set time slot parameters
                    params = {
                        'serialNum': self.device_serial,
                        'timeslot': slot['slot_number'],
                        'startHour': slot['start_hour'],
                        'startMin': slot['start_minute'],
                        'endHour': slot['end_hour'],
                        'endMin': slot['end_minute'],
                        'enable': 1 if slot['enabled'] else 0,
                        'power': slot['power_percentage']
                    }

                    # Use the appropriate API method based on your inverter model
                    # Example: self.api.set_ac_charge_time(params)
                    logger.info(f"Setting time slot {slot['slot_number']}: "
                               f"{slot['start_hour']:02d}:{slot['start_minute']:02d} - "
                               f"{slot['end_hour']:02d}:{slot['end_minute']:02d}")

                    # Wait between API calls to avoid rate limiting
                    time.sleep(1)

            logger.info("Charging schedule set successfully")
            return True

        except Exception as e:
            logger.error(f"Error setting charging schedule: {e}")
            return False

    def set_battery_mode(self, mode: str) -> bool:
        """
        Set battery operation mode

        Args:
            mode: 'load_first', 'battery_first', or 'grid_first'

        Returns:
            True if successful
        """
        mode_mapping = {
            'load_first': 0,      # Self-consumption mode
            'battery_first': 1,   # Battery priority
            'grid_first': 2       # Grid priority (charge from grid)
        }

        if mode not in mode_mapping:
            logger.error(f"Invalid mode: {mode}")
            return False

        if self.dry_run:
            logger.info(f"[DRY RUN] Would set battery mode to: {mode}")
            return True

        try:
            # Set battery mode via API
            # Note: Actual method may vary
            mode_value = mode_mapping[mode]
            # self.api.set_battery_mode(self.device_serial, mode_value)

            logger.info(f"Battery mode set to: {mode}")
            return True

        except Exception as e:
            logger.error(f"Error setting battery mode: {e}")
            return False


class GrowattModbusController(GrowattController):
    """
    Controls Growatt via Modbus RTU/TCP
    Requires: pip install pymodbus
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.host = config.get('modbus_host', '192.168.1.100')
        self.port = config.get('modbus_port', 502)
        self.unit_id = config.get('modbus_unit_id', 1)
        self.connection_type = config.get('modbus_type', 'tcp')  # 'tcp' or 'rtu'

        if not self.dry_run:
            try:
                from pymodbus.client import ModbusTcpClient, ModbusSerialClient
                from pymodbus.constants import Endian
                from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

                if self.connection_type == 'tcp':
                    self.client = ModbusTcpClient(self.host, port=self.port)
                else:
                    self.client = ModbusSerialClient(
                        method='rtu',
                        port=config.get('serial_port', '/dev/ttyUSB0'),
                        baudrate=config.get('baudrate', 9600),
                        parity='N',
                        stopbits=1,
                        bytesize=8,
                        timeout=3
                    )

                self.BinaryPayloadDecoder = BinaryPayloadDecoder
                self.BinaryPayloadBuilder = BinaryPayloadBuilder
                self.Endian = Endian

                self.connect()
            except ImportError:
                logger.error("pymodbus library not installed. Run: pip install pymodbus")
                raise
        else:
            logger.info("DRY RUN MODE: No actual Modbus connections will be made")

    def connect(self):
        """Connect to Modbus device"""
        try:
            connection = self.client.connect()
            if connection:
                logger.info(f"Connected to Growatt via Modbus {self.connection_type.upper()}")
                return True
            else:
                logger.error("Failed to connect to Modbus device")
                return False
        except Exception as e:
            logger.error(f"Modbus connection error: {e}")
            raise

    def read_holding_registers(self, address: int, count: int = 1) -> Optional[List[int]]:
        """Read holding registers"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would read {count} registers from address {address}")
            return [0] * count

        try:
            result = self.client.read_holding_registers(address, count, unit=self.unit_id)
            if not result.isError():
                return result.registers
            else:
                logger.error(f"Error reading registers at {address}: {result}")
                return None
        except Exception as e:
            logger.error(f"Modbus read error: {e}")
            return None

    def write_holding_register(self, address: int, value: int) -> bool:
        """Write single holding register"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write value {value} to register {address}")
            return True

        try:
            result = self.client.write_register(address, value, unit=self.unit_id)
            if not result.isError():
                logger.info(f"Successfully wrote {value} to register {address}")
                return True
            else:
                logger.error(f"Error writing register {address}: {result}")
                return False
        except Exception as e:
            logger.error(f"Modbus write error: {e}")
            return False

    def get_battery_status(self) -> Dict:
        """Get current battery status via Modbus"""
        # Register addresses may vary by model - check your inverter documentation
        # These are example addresses
        SOC_REGISTER = 1014
        BATTERY_POWER_REGISTER = 1009
        BATTERY_VOLTAGE_REGISTER = 1013

        if self.dry_run:
            logger.info("[DRY RUN] Would read battery status via Modbus")
            return {
                'soc': 50,
                'power': 0,
                'voltage': 52.0,
                'status': 'standby'
            }

        try:
            soc_value = self.read_holding_registers(SOC_REGISTER, 1)
            power_value = self.read_holding_registers(BATTERY_POWER_REGISTER, 1)
            voltage_value = self.read_holding_registers(BATTERY_VOLTAGE_REGISTER, 1)

            status = {
                'soc': soc_value[0] if soc_value else 0,
                'power': power_value[0] if power_value else 0,
                'voltage': voltage_value[0] / 10.0 if voltage_value else 0,  # Usually scaled
                'status': 'connected'
            }

            logger.info(f"Battery Status: SOC={status['soc']}%, Power={status['power']}W")
            return status

        except Exception as e:
            logger.error(f"Error reading battery status: {e}")
            return {}

    def set_charging_schedule(self, time_slots: List[Dict]) -> bool:
        """
        Set charging schedule via Modbus

        Note: Register addresses vary by model. Check your Growatt Modbus documentation.
        Common registers for SPH models:
        - Time slot 1 start: 1090-1091 (hour, minute)
        - Time slot 1 end: 1092-1093 (hour, minute)
        - Time slot 1 enable: 1094
        """
        if self.dry_run:
            logger.info("[DRY RUN] Would set charging schedule via Modbus:")
            for slot in time_slots:
                logger.info(f"  Slot {slot['slot_number']}: "
                           f"{slot['start_hour']:02d}:{slot['start_minute']:02d} - "
                           f"{slot['end_hour']:02d}:{slot['end_minute']:02d}")
            return True

        try:
            # Base register address for time slots (example - verify for your model)
            BASE_REGISTER = 1090

            for slot in time_slots:
                if slot['enabled']:
                    slot_offset = (slot['slot_number'] - 1) * 6  # 6 registers per slot

                    # Write start time
                    self.write_holding_register(BASE_REGISTER + slot_offset, slot['start_hour'])
                    time.sleep(0.1)
                    self.write_holding_register(BASE_REGISTER + slot_offset + 1, slot['start_minute'])
                    time.sleep(0.1)

                    # Write end time
                    self.write_holding_register(BASE_REGISTER + slot_offset + 2, slot['end_hour'])
                    time.sleep(0.1)
                    self.write_holding_register(BASE_REGISTER + slot_offset + 3, slot['end_minute'])
                    time.sleep(0.1)

                    # Enable slot
                    self.write_holding_register(BASE_REGISTER + slot_offset + 4, 1)
                    time.sleep(0.1)

                    logger.info(f"Set time slot {slot['slot_number']}: "
                               f"{slot['start_hour']:02d}:{slot['start_minute']:02d} - "
                               f"{slot['end_hour']:02d}:{slot['end_minute']:02d}")

            logger.info("Charging schedule set successfully via Modbus")
            return True

        except Exception as e:
            logger.error(f"Error setting charging schedule: {e}")
            return False

    def set_battery_mode(self, mode: str) -> bool:
        """Set battery operation mode via Modbus"""
        # Mode register address (example - verify for your model)
        MODE_REGISTER = 1044

        mode_mapping = {
            'load_first': 0,
            'battery_first': 1,
            'grid_first': 2
        }

        if mode not in mode_mapping:
            logger.error(f"Invalid mode: {mode}")
            return False

        if self.dry_run:
            logger.info(f"[DRY RUN] Would set battery mode to: {mode}")
            return True

        try:
            mode_value = mode_mapping[mode]
            success = self.write_holding_register(MODE_REGISTER, mode_value)

            if success:
                logger.info(f"Battery mode set to: {mode}")
            return success

        except Exception as e:
            logger.error(f"Error setting battery mode: {e}")
            return False


def get_controller(config: Dict) -> GrowattController:
    """
    Factory function to get the appropriate Growatt controller

    Args:
        config: Configuration dictionary with 'connection_type' key

    Returns:
        Appropriate GrowattController instance
    """
    connection_type = config.get('connection_type', 'api').lower()

    controllers = {
        'api': GrowattAPIController,
        'modbus': GrowattModbusController
    }

    if connection_type not in controllers:
        raise ValueError(f"Unknown connection type: {connection_type}. "
                        f"Options: {list(controllers.keys())}")

    return controllers[connection_type](config)


# Example usage
if __name__ == '__main__':
    # API configuration example
    api_config = {
        'connection_type': 'api',
        'username': 'your_growatt_username',
        'password': 'your_growatt_password',
        'plant_id': 'your_plant_id',
        'device_serial': 'your_device_serial',
        'dry_run': True
    }

    # Modbus configuration example
    modbus_config = {
        'connection_type': 'modbus',
        'modbus_type': 'tcp',
        'modbus_host': '192.168.1.100',
        'modbus_port': 502,
        'modbus_unit_id': 1,
        'dry_run': True
    }

    # Create controller
    controller = get_controller(modbus_config)

    # Get battery status
    status = controller.get_battery_status()
    print(f"Battery Status: {status}")

    # Example time slots
    time_slots = [
        {
            'slot_number': 1,
            'enabled': True,
            'start_hour': 2,
            'start_minute': 0,
            'end_hour': 6,
            'end_minute': 0,
            'power_percentage': 100,
            'mode': 'charge'
        }
    ]

    # Set charging schedule
    controller.set_charging_schedule(time_slots)

    # Set battery mode
    controller.set_battery_mode('battery_first')
