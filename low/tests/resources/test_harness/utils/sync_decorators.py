"""sync decorators."""
import functools
import logging
import os
from contextlib import contextmanager

from ska_ser_logging import configure_logging
from tests.resources.test_harness.constant import (
    low_centralnode,
    low_csp_master,
    low_csp_subarray_leaf_prefix,
    low_csp_subarray_prefix,
    low_sdp_master,
    low_sdp_subarray_leaf_prefix,
    low_sdp_subarray_prefix,
    mccs_controller,
    mccs_master_leaf_node,
    mccs_subarray_leaf_prefix,
    mccs_subarray_prefix,
    tmc_low_subarray_prefix,
)
from tests.resources.test_harness.utils.wait_helpers import Waiter
from tests.resources.test_support.common_utils.base_utils import DeviceUtils
from tests.resources.test_support.common_utils.common_helpers import Resource

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

MCCS_SIMULATION_ENABLED = os.getenv("MCCS_SIMULATION_ENABLED")
if MCCS_SIMULATION_ENABLED.lower() == "false":
    TIMEOUT = 600  # MCCS lower level devices take more time to turn on and off
else:
    TIMEOUT = 500


def sync_set_to_on(device_dict: dict):
    """sync decorators method"""

    def decorator_sync_set_to_on(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_telescope_on()
            result = func(*args, **kwargs)
            the_waiter.wait(TIMEOUT)
            return result

        return wrapper

    return decorator_sync_set_to_on


def sync_set_to_off(device_dict: dict):
    def decorator_sync_set_to_off(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_off()
            result = func(*args, **kwargs)
            the_waiter.wait(TIMEOUT)
            return result

        return wrapper

    return decorator_sync_set_to_off


# defined as a context manager
@contextmanager
def sync_going_to_off(timeout=50, **kwargs):
    the_waiter = Waiter(**kwargs)
    the_waiter.set_wait_for_going_to_off()
    yield
    the_waiter.wait(timeout)


def sync_set_to_standby(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        the_waiter = Waiter(**kwargs)
        the_waiter.set_wait_for_going_to_standby()
        result = func(*args, **kwargs)
        the_waiter.wait(TIMEOUT)
        return result

    return wrapper


def sync_release_resources(timeout=200):
    def decorator_sync_release_resources(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            subarray_id = args[2]
            device_dict = get_low_devices_dictionary(subarray_id)
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_empty()
            result = func(*args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_release_resources


def sync_assign_resources():
    # defined as a decorator
    def decorator_sync_assign_resources(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            subarray_id = args[2]
            device_dict = get_low_devices_dictionary(subarray_id)
            device = DeviceUtils(
                obs_state_device_names=[
                    device_dict.get("csp_subarray"),
                    device_dict.get("sdp_subarray"),
                    device_dict.get("tmc_subarraynode"),
                ]
            )
            device.check_devices_obsState("EMPTY")
            set_wait_for_obsstate = kwargs.get("set_wait_for_obsstate", True)
            result = func(*args, **kwargs)
            if set_wait_for_obsstate:
                the_waiter = Waiter(**device_dict)
                the_waiter.set_wait_for_assign_resources()
                the_waiter.wait(700)
            return result

        return wrapper

    return decorator_sync_assign_resources


def sync_abort(timeout=1000):
    # define as a decorator
    def decorator_sync_abort(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            subarray_id = args[1]
            device_dict = get_low_devices_dictionary(subarray_id)
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_aborted()
            result = func(*args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_abort


def sync_restart(timeout=500):
    # define as a decorator
    def decorator_sync_restart(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            subarray_id = args[1]
            device_dict = get_low_devices_dictionary(subarray_id)
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_empty()
            result = func(*args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_restart


def sync_configure():
    # defined as a decorator
    def decorator_sync_configure(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            invoked_from_ready = False
            subarray_id = args[2]
            device_dict = get_low_devices_dictionary(subarray_id)
            the_waiter = Waiter(**device_dict)
            if Resource(device_dict.get("tmc_subarraynode")) == "READY":
                invoked_from_ready = True
            result = func(*args, **kwargs)
            if invoked_from_ready:
                the_waiter.set_wait_for_configuring()
                the_waiter.wait(500)
            the_waiter.set_wait_for_configure()
            the_waiter.wait(800)
            return result

        return wrapper

    return decorator_sync_configure


def sync_end():
    # defined as a decorator
    def decorator_sync_end(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            subarray_id = args[1]
            device_dict = get_low_devices_dictionary(subarray_id)
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_idle()
            result = func(*args, **kwargs)
            the_waiter.wait(500)
            return result

        return wrapper

    return decorator_sync_end


def sync_endscan():
    # defined as a decorator
    def decorator_sync_endscan(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            subarray_id = args[1]
            device_dict = get_low_devices_dictionary(subarray_id)
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_ready()
            result = func(*args, **kwargs)
            the_waiter.wait(200)
            return result

        return wrapper

    return decorator_sync_endscan


def get_low_devices_dictionary(subarray_id: str):
    """Helper method to provide the dictionary with Low Telescope devices
    for given Subarray Id"""
    devices_dict = {}
    devices_dict[
        "tmc_subarraynode"
    ] = tmc_low_subarray_prefix + subarray_id.zfill(2)
    devices_dict["sdp_subarray"] = low_sdp_subarray_prefix + subarray_id.zfill(
        2
    )
    devices_dict["csp_subarray"] = low_csp_subarray_prefix + subarray_id.zfill(
        2
    )
    devices_dict[
        "sdp_subarray_leaf_node"
    ] = low_sdp_subarray_leaf_prefix + subarray_id.zfill(2)
    devices_dict[
        "csp_subarray_leaf_node"
    ] = low_csp_subarray_leaf_prefix + subarray_id.zfill(2)
    devices_dict[
        "mccs_subarray_leaf_node"
    ] = mccs_subarray_leaf_prefix + subarray_id.zfill(2)
    devices_dict["mccs_subarray"] = mccs_subarray_prefix + subarray_id.zfill(2)
    devices_dict["csp_master"] = low_csp_master
    devices_dict["sdp_master"] = low_sdp_master
    devices_dict["mccs_master"] = mccs_controller
    devices_dict["mccs_master_leaf_node"] = mccs_master_leaf_node
    devices_dict["central_node"] = low_centralnode
    return devices_dict
