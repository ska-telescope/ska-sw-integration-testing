"""A Class related to simulator device
"""
import logging

from ska_ser_logging import configure_logging
from tango import DeviceProxy

from tests.resources.test_harness.constant import SIMULATOR_DEVICE_FQDN_DICT
from tests.resources.test_harness.utils.enums import SimulatorDeviceType

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class SimulatorFactory:
    """This Simulator factory used to implement method for creating
    Tango simulator(sim) object for Low Telescope.
    """

    def __init__(self):
        """Initialize sim object dict"""
        self._sim_dev = {}

    def get_or_create_simulator_device(
        self,
        device_type: SimulatorDeviceType,
        sim_number: int = 1,
    ) -> DeviceProxy:
        """This method create or get simulator object
        based on device type provided

        Args:
            device_type (str): Device type for which Simulator need
            to be created
            sim_number (int): Simulator number device proxy object to return.
            Default return 1st Simulator device
        Returns:
            sim_device_proxy: Device Proxy of simulator device
        """
        if device_type in self._sim_dev:
            LOGGER.info(f"Found existing simulator device for {device_type}")
            sim_device = self._sim_dev[device_type][sim_number]
        else:
            sim_fqdn_list = SIMULATOR_DEVICE_FQDN_DICT.get(device_type)
            LOGGER.info(f"Initializing simulator device for {sim_fqdn_list}")
            self._sim_dev[device_type] = {}
            for index, mock_fqdn in enumerate(sorted(sim_fqdn_list), start=1):
                device = DeviceProxy(mock_fqdn)
                self._sim_dev[device_type][index] = device
            sim_device = self._sim_dev[device_type][sim_number]

        return sim_device
