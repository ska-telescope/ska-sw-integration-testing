"""State Control module -local depedencies"""
from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.common_helpers import Resource


class BaseTelescopeControl:
    """Base Telescope control class.
    Use this class to write method to check status of devices
    """

    def is_in_valid_state(self, device_state_info, state_str):
        """Validate device state is in desired state as per device state info
        Args:
            device_state_info (dict): device name and it's expected state info
        """
        state_result_list = []
        for device in device_state_info:
            state_list = device_state_info.get(device)
            device_state = Resource(device).get(state_str)
            LOGGER.info(
                f"Resource({device}).get('{state_str}') : {device_state}"
            )
            state_result_list.append(
                Resource(device).get(state_str) in state_list
            )

        return all(state_result_list)


def check_subarray1_availability(subarray_devname):
    """Checks subarray availability"""
    subarray1_availability = Resource(subarray_devname).get(
        "isSubarrayAvailable"
    )
    LOGGER.info(
        f"{subarray_devname}.isSubarrayAvailable : "
        + str(subarray1_availability)
    )

    return subarray1_availability
