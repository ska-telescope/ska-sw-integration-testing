import logging
from datetime import datetime

from ska_ser_logging import configure_logging

from tests.resources.test_support.common_utils.common_helpers import (
    AttributeWatcher,
    Resource,
    watch,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


# this is a composite type of waiting based on a set of predefined
# pre conditions expected to be true
class Waiter:
    def __init__(self, **kwargs):
        """
        Args:
            kwargs (dict): device names
        """
        self.waits = []
        self.logs = ""
        self.error_logs = ""
        self.timed_out = False
        self.sdp_subarray1 = kwargs.get("sdp_subarray")
        self.sdp_master = kwargs.get("sdp_master")
        self.csp_subarray1 = kwargs.get("csp_subarray")
        self.csp_master = kwargs.get("csp_master")
        self.tmc_subarraynode1 = kwargs.get("tmc_subarraynode")
        self.tmc_csp_subarray_leaf_node = kwargs.get("csp_subarray_leaf_node")
        self.tmc_mccs_subarray_leaf_node = kwargs.get(
            "mccs_subarray_leaf_node"
        )
        self.tmc_sdp_subarray_leaf_node = kwargs.get("sdp_subarray_leaf_node")
        self.cbf_subarray1 = kwargs.get("cbf_subarray1")
        self.cbf_controller = kwargs.get("cbf_controller")
        self.mccs_subarray = kwargs.get("mccs_subarray")
        self.central_node = kwargs.get("central_node")
        self.mccs_master = kwargs.get("mccs_master")

    def clear_watches(self):
        self.waits = []

    def set_wait_for_going_to_off(self):
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_master)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_master)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.central_node)).to_become(
                "telescopeState", changed_to="OFF"
            )
        )

        self.waits.append(
            watch(Resource(self.mccs_master)).to_become(
                "State", changed_to="OFF"
            )
        )

    def set_wait_for_going_to_standby(self):
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_master)).to_become(
                "State", changed_to="STANDBY"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_master)).to_become(
                "State", changed_to="STANDBY"
            )
        )

    def set_wait_for_telescope_on(self):
        self.waits.append(
            watch(Resource(self.sdp_master)).to_become(
                "State", changed_to="ON"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "State", changed_to="ON"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_master)).to_become(
                "State", changed_to="ON"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "State", changed_to="ON"
            )
        )

        self.waits.append(
            watch(Resource(self.mccs_subarray)).to_become(
                "State", changed_to="ON"
            )
        )
        self.waits.append(
            watch(Resource(self.mccs_master)).to_become(
                "State", changed_to="ON"
            )
        )

        if self.cbf_subarray1:
            watch(Resource(self.cbf_subarray1)).to_become(
                "State", changed_to="ON"
            )
        if self.cbf_controller:
            watch(Resource(self.cbf_controller)).to_become(
                "State", changed_to="ON"
            )
            watch(Resource(self.cbf_controller)).to_become(
                "reportVccState", changed_to="[0, 0, 0, 0]"
            )
        self.waits.append(
            watch(Resource(self.central_node)).to_become(
                "telescopeState", changed_to="ON"
            )
        )

    def set_wait_for_going_to_empty(self):
        self.waits.append(
            watch(Resource(self.tmc_csp_subarray_leaf_node)).to_become(
                "cspSubarrayObsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_sdp_subarray_leaf_node)).to_become(
                "sdpSubarrayObsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "assignedResources", changed_to=None
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_mccs_subarray_leaf_node)).to_become(
                "obsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="EMPTY"
            )
        )

    def set_wait_for_assign_resources(self):
        self.waits.append(
            watch(Resource(self.tmc_csp_subarray_leaf_node)).to_become(
                "cspSubarrayObsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_sdp_subarray_leaf_node)).to_become(
                "sdpSubarrayObsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_mccs_subarray_leaf_node)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )

        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )

    def set_wait_for_configuring(self):
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="CONFIGURING"
            )
        )

    def set_wait_for_obs_state(self, obs_state=None):
        self.waits.append(
            watch(Resource(self.tmc_csp_subarray_leaf_node)).to_become(
                "cspSubarrayObsState", changed_to=obs_state
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_sdp_subarray_leaf_node)).to_become(
                "sdpSubarrayObsState", changed_to=obs_state
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to=obs_state
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to=obs_state
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_mccs_subarray_leaf_node)).to_become(
                "obsState", changed_to=obs_state
            )
        )

        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to=obs_state
            )
        )

    def set_wait_for_configure(self):
        self.waits.append(
            watch(Resource(self.tmc_csp_subarray_leaf_node)).to_become(
                "cspSubarrayObsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_sdp_subarray_leaf_node)).to_become(
                "sdpSubarrayObsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_mccs_subarray_leaf_node)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )

        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="READY"
            )
        )

    def set_wait_for_idle(self):
        self.waits.append(
            watch(Resource(self.tmc_csp_subarray_leaf_node)).to_become(
                "cspSubarrayObsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_sdp_subarray_leaf_node)).to_become(
                "sdpSubarrayObsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_mccs_subarray_leaf_node)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )

    def set_wait_for_aborted(self):
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="ABORTED"
            )
        )

    def set_wait_for_ready(self):
        self.waits.append(
            watch(Resource(self.tmc_csp_subarray_leaf_node)).to_become(
                "cspSubarrayObsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_sdp_subarray_leaf_node)).to_become(
                "sdpSubarrayObsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_mccs_subarray_leaf_node)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="READY"
            )
        )

    def set_wait_for_specific_obsstate(self, obsstate: str, devices: list):
        """Waits for the obsState of given devices
        to change to specified value."""
        for device in devices:
            self.waits.append(
                watch(Resource(device)).to_become(
                    "obsState", changed_to=obsstate
                )
            )

    def set_wait_for_scanning(self):
        self.waits.append(
            watch(Resource(self.tmc_csp_subarray_leaf_node)).to_become(
                "cspSubarrayObsState", changed_to="SCANNING"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_sdp_subarray_leaf_node)).to_become(
                "sdpSubarrayObsState", changed_to="SCANNING"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_mccs_subarray_leaf_node)).to_become(
                "obsState", changed_to="SCANNING"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="SCANNING"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="SCANNING"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="SCANNING"
            )
        )

    def wait(self, timeout=30, resolution=0.1):
        self.logs = ""
        while self.waits:
            wait = self.waits.pop()
            if isinstance(wait, AttributeWatcher):
                timeout = timeout * resolution
            try:
                result = wait.wait_until_conditions_met(timeout=timeout)
            except Exception as ex:
                self.timed_out = True
                future_value_shim = ""
                timeout_shim = timeout * resolution
                if isinstance(wait, AttributeWatcher):
                    timeout_shim = timeout
                if wait.future_value is not None:
                    future_value_shim = f" to {wait.future_value} \
                        (current val={wait.current_value})"
                self.error_logs += "{} timed out whilst waiting for {} to \
                change from {}{} in {:f}s and raised {}\n".format(
                    wait.device_name,
                    wait.attr,
                    wait.previous_value,
                    future_value_shim,
                    timeout_shim,
                    ex,
                )
                LOGGER.error(
                    "Exception occurred at %s with error: %s",
                    datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S:%f"),
                    self.error_logs,
                )
            else:
                timeout_shim = (timeout - result) * resolution
                if isinstance(wait, AttributeWatcher):
                    timeout_shim = result
                self.logs += (
                    "{} changed {} from {} to {} after {:f}s \n".format(
                        wait.device_name,
                        wait.attr,
                        wait.previous_value,
                        wait.current_value,
                        timeout_shim,
                    )
                )
        if self.timed_out:
            raise Exception(
                "timed out, the following timeouts ocurred:\n{} Successful\
                      changes:\n{}".format(
                    self.error_logs, self.logs
                )
            )
