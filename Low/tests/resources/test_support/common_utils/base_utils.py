"""
Simple class for checking device ObsState
"""
<<<<<<< HEAD
from Low.tests.resources.test_support.common_utils.common_helpers import (
    Resource,
)
=======
from tests.resources.test_support.common_utils.common_helpers import Resource
>>>>>>> 891ce57dcad70fd26997252a96b4b9ff6215086a


class DeviceUtils:
    """This class implement method for checking obsState of provided devices"""

    def __init__(self, **kwargs):
        """
        Args:
            kwargs (dict) - provide list of devices to check for obsState as
            value in dict
        """
        self.obs_state_device_names = kwargs.get("obs_state_device_names", [])

    def check_devices_obsState(self, obs_state) -> None:
        """
        Args:
            obs_state (str): ObsState to check for device
        """
        for device_name in self.obs_state_device_names:
            Resource(device_name).assert_attribute("obsState").equals(
                obs_state
            )
