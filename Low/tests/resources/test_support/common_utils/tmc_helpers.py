"""This module implement base helper class for tmc
"""
import json
import logging
import time
from typing import Optional, Tuple

from assertpy import assert_that
from ska_control_model import ObsState, ResultCode
from ska_ser_logging import configure_logging
from tango import DeviceProxy, DevState

from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.resources.test_support.common_utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_assigning,
    sync_configure,
    sync_configure_sub,
    sync_end,
    sync_endscan,
    sync_endscan_in_ready,
    sync_release_resources,
    sync_restart,
    sync_scan,
    sync_set_to_off,
    sync_set_to_standby,
    sync_telescope_on,
)
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.constant_low import (
    DEVICE_OBS_STATE_ABORT_INFO as LOW_OBS_STATE_ABORT_INFO,
)
from tests.resources.test_support.constant_low import (
    DEVICE_OBS_STATE_EMPTY_INFO as LOW_OBS_STATE_EMPTY_INFO,
)
from tests.resources.test_support.constant_low import (
    DEVICE_OBS_STATE_IDLE_INFO as LOW_OBS_STATE_IDLE_INFO,
)
from tests.resources.test_support.constant_low import (
    DEVICE_STATE_STANDBY_INFO as LOW_OBS_STATE_STANDBY_INFO,
)
from tests.resources.test_support.constant_low import (
    INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT,
    INTERMEDIATE_STATE_DEFECT,
)
from tests.resources.test_support.constant_low import (
    csp_subarray1 as csp_subarray1_low,
)
from tests.resources.test_support.constant_low import (
    sdp_subarray1 as sdp_subarray1_low,
)

TIMEOUT = 20
configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class TmcHelper:
    """TmcHelper class"""

    def __init__(self, central_node, subarray_node) -> None:
        """
        Args:
            central_node (str) -> FQDN of Central Node
        """
        self.centralnode = central_node
        self.subarray_node = subarray_node

    def check_devices(self, device_list: list) -> None:
        """
        Args:
            device_list (list): List of devices to check if it is ON.
        """
        for device in device_list:
            device_proxy = DeviceProxy(device)
            assert 0 < device_proxy.ping()

    def check_telescope_availability(self) -> None:
        """
        Checks of Telescope availability is set to True
        CSP , SDP Master should be True
        At least one of the Subarray node should be available
        """
        # Check if at least 1 subarry node is true

        central_node = DeviceProxy(self.centralnode)
        telescopeavailability = central_node.read_attribute(
            "telescopeAvailability"
        ).value
        telescopeavailability = json.loads(telescopeavailability)
        # provides key as subarray's and their availability
        # we are just checking only availability
        for _, availability in telescopeavailability["tmc_subarrays"].items():
            assert availability

        # Check if CSP/SDP master nodes are true in telescopeavailability

        assert telescopeavailability["csp_master_leaf_node"]
        assert telescopeavailability["sdp_master_leaf_node"]

    @sync_telescope_on
    def set_to_on(self, **kwargs: dict) -> None:
        """
        Sets telescope to on
        Args:
            kwargs (dict): device info which needs set to ON
        """

        central_node = DeviceProxy(self.centralnode)
        LOGGER.info(
            "Before Sending TelescopeOn command %s\
            State is: %s",
            central_node,
            central_node.State(),
        )
        central_node.TelescopeOn()
        device_to_on_list = [
            kwargs.get("csp_subarray"),
            kwargs.get("sdp_subarray"),
        ]
        for device in device_to_on_list:
            if device:
                device_proxy = DeviceProxy(device)
                device_proxy.SetDirectState(DevState.ON)

    @sync_set_to_off
    def set_to_off(self, **kwargs: dict) -> None:
        """
        Sets telescope to off
        Args:
            kwargs (dict): device info which needs set to ON
        """
        central_node = DeviceProxy(self.centralnode)
        central_node.TelescopeOff()
        device_to_off_list = [
            kwargs.get("csp_subarray"),
            kwargs.get("sdp_subarray"),
        ]
        for device in device_to_off_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(DevState.OFF)

        LOGGER.info(
            "After invoking TelescopeOff command %s  State is:\
            %s ",
            central_node,
            central_node.State(),
        )

    @sync_set_to_standby
    def set_to_standby(self, **kwargs: dict) -> None:
        """
        Sets telescope to standby
        Args:
            kwargs (dict): device info which needs set to ON
        """
        central_node = DeviceProxy(self.centralnode)
        central_node.TelescopeStandBy()
        device_to_standby_list = [
            kwargs.get("csp_subarray"),
            kwargs.get("sdp_subarray"),
        ]
        for device in device_to_standby_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(DevState.OFF)
            # TODO: move this to proper place
            device_proxy.ClearCommandCallInfo()

        LOGGER.info(
            "After invoking TelescopeStandBy command %s  State is:\
            %s ",
            central_node,
            central_node.State(),
        )

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_release_resources()
    def invoke_releaseResources(
        self, release_input_str: str, **kwargs: dict
    ) -> Tuple[ResultCode, str]:
        """
        Invokes releaseResources
        Args:
            release_input_str(str): json input string
            kwargs (dict): device info which needs set to ON
        """
        central_node = DeviceProxy(self.centralnode)
        result, message = central_node.ReleaseResources(release_input_str)
        LOGGER.info("ReleaseResources command is invoked on %s", central_node)
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_assign_resources()
    def compose_sub(
        self, assign_res_input: str, **kwargs: dict
    ) -> Tuple[ResultCode, str]:
        """Invokes assignResources on central node"""
        Resource(self.subarray_node).assert_attribute("State").equals("ON")
        Resource(self.subarray_node).assert_attribute("obsState").equals(
            "EMPTY"
        )
        central_node = DeviceProxy(self.centralnode)
        result, message = central_node.AssignResources(assign_res_input)
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_configure()
    def configure_subarray(self, configure_input_str: str, **kwargs: dict):
        """Invokes configure on subarray node"""
        subarray_node = DeviceProxy(self.subarray_node)
        result, message = subarray_node.Configure(configure_input_str)
        LOGGER.info("Invoked Configure on SubarrayNode")
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_scan()
    def scan(
        self, scan_input_str: str, **kwargs: dict
    ) -> Tuple[ResultCode, str]:
        """Invokes scan command on subarray node"""
        subarray_node = DeviceProxy(self.subarray_node)
        result, message = subarray_node.Scan(scan_input_str)
        LOGGER.info("Invoked Scan on SubarrayNode")
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_end()
    def end(self, **kwargs: dict) -> Tuple[ResultCode, str]:
        """Invokes end command on subarray node"""
        subarray_node = DeviceProxy(self.subarray_node)
        result, message = subarray_node.End()
        LOGGER.info("End command is invoked on %s", subarray_node)
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_abort()
    def invoke_abort(self, **kwargs: dict) -> Tuple[ResultCode, str]:
        """Invokes abort command on subarray node"""
        subarray_node = DeviceProxy(self.subarray_node)
        result, message = subarray_node.Abort()
        LOGGER.info("Invoked Abort on SubarrayNode")
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_restart()
    def invoke_restart(self, **kwargs: dict) -> Tuple[ResultCode, str]:
        """Invokes restart command on subarray node"""
        subarray_node = DeviceProxy(self.subarray_node)
        subarray_node.Restart()
        LOGGER.info("Invoked Restart on SubarrayNode")

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_assigning()
    def assign_resources(
        self, assign_res_input, **kwargs: dict
    ) -> Tuple[ResultCode, str]:
        """Invokes assign resources command on central node"""
        Resource(self.subarray_node).assert_attribute("State").equals("ON")
        central_node = DeviceProxy(self.centralnode)
        result, message = central_node.AssignResources(assign_res_input)
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_configure_sub()
    def configure_sub(
        self, configure_input_str: str, **kwargs: dict
    ) -> Tuple[ResultCode, str]:
        """Invokes configure command on subarray node"""
        Resource(self.subarray_node).assert_attribute("obsState").equals(
            "IDLE"
        )
        subarray_node = DeviceProxy(self.subarray_node)
        result, message = subarray_node.Configure(configure_input_str)
        LOGGER.info("Invoked Configure on SubarrayNode")
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_endscan()
    def invoke_endscan(self, **kwargs: dict) -> Tuple[ResultCode, str]:
        """Invokes endscan command on subarray node"""
        subarray_node = DeviceProxy(self.subarray_node)
        result, message = subarray_node.EndScan()
        LOGGER.info("Invoked EndScan on SubarrayNode")
        return result, message

    # **kwargs is used by decorator
    # pylint: disable=unused-argument
    @sync_endscan_in_ready()
    def invoke_endscan_in_ready(
        self, **kwargs: dict
    ) -> Tuple[ResultCode, str]:
        """Invokes endscan command on subarray node in READY obstate"""
        subarray_node = DeviceProxy(self.subarray_node)
        result, message = subarray_node.EndScan()
        LOGGER.info("Invoked EndScan on SubarrayNode")
        return result, message


def wait_for_attribute_update(
    device, attribute_name: str, expected_id: str, expected_result: ResultCode
):
    """Wait for the attribute to reflect necessary changes."""
    start_time = time.time()
    elapsed_time = time.time() - start_time
    while elapsed_time <= TIMEOUT:
        unique_id, result = device.read_attribute(attribute_name).value
        if expected_id in unique_id:
            LOGGER.info("The attribute value is: %s, %s", unique_id, result)
            return json.loads(result)[0] == expected_result
        time.sleep(1)
        elapsed_time = time.time() - start_time
    return False


def tear_down(
    input_json: Optional[str] = None,
    raise_exception: Optional[bool] = True,
    **kwargs,
):
    """Tears down the system after test run to get telescope back in \
        standby state."""

    LOGGER.info("Calling tear down")
    subarray_node_obsstate = Resource(kwargs.get("tmc_subarraynode")).get(
        "obsState"
    )
    tmc_helper = TmcHelper(
        kwargs.get("central_node"), kwargs.get("tmc_subarraynode")
    )
    telescope_control = BaseTelescopeControl()
    DEVICE_LIST = [
        kwargs.get("sdp_subarray"),
        kwargs.get("csp_subarray"),
    ]
    ABORT_INFO = LOW_OBS_STATE_ABORT_INFO
    EMPTY_INFO = LOW_OBS_STATE_EMPTY_INFO
    IDLE_INFO = LOW_OBS_STATE_IDLE_INFO
    STANDBY_INFO = LOW_OBS_STATE_STANDBY_INFO
    if subarray_node_obsstate in ["RESOURCING", "CONFIGURING", "SCANNING"]:
        LOGGER.info("Invoking Abort on TMC")

        tmc_helper.invoke_abort(**kwargs)
        LOGGER.info("Invoking Abort command on TMC SubarrayNode")
        assert telescope_control.is_in_valid_state(ABORT_INFO, "obsState")

        tmc_helper.invoke_restart(**kwargs)
        LOGGER.info("Invoking Restart command on TMC SubarrayNode")
        assert telescope_control.is_in_valid_state(EMPTY_INFO, "obsState")

        tmc_helper.set_to_standby(**kwargs)
        LOGGER.info("Invoking Standby command on TMC SubarrayNode")
        assert telescope_control.is_in_valid_state(STANDBY_INFO, "State")

        LOGGER.info("Tear Down complete. Telescope is in Standby State")

    elif subarray_node_obsstate == "EMPTY":
        LOGGER.info("Invoking Standby command on TMC SubarrayNode")
        tmc_helper.set_to_standby(**kwargs)
        assert telescope_control.is_in_valid_state(STANDBY_INFO, "State")

        LOGGER.info("Tear Down complete. Telescope is in Standby State")

    elif subarray_node_obsstate == "IDLE":
        LOGGER.info("Invoking ReleaseResources command on TMC SubarrayNode")
        tmc_helper.invoke_releaseResources(input_json, **kwargs)
        assert telescope_control.is_in_valid_state(EMPTY_INFO, "obsState")

        LOGGER.info("Invoking Standby command on TMC SubarrayNode")
        tmc_helper.set_to_standby(**kwargs)
        assert telescope_control.is_in_valid_state(STANDBY_INFO, "State")

        LOGGER.info("Tear Down complete. Telescope is in Standby State")

    elif subarray_node_obsstate == "READY":
        LOGGER.info("Invoking End command on TMC SubarrayNode")
        tmc_helper.end(**kwargs)
        assert telescope_control.is_in_valid_state(IDLE_INFO, "obsState")

        LOGGER.info("Invoking ReleaseResources command on TMC SubarrayNode")
        tmc_helper.invoke_releaseResources(input_json, **kwargs)
        assert telescope_control.is_in_valid_state(EMPTY_INFO, "obsState")

        LOGGER.info("Invoking Standby command on TMC SubarrayNode")
        tmc_helper.set_to_standby(**kwargs)
        assert telescope_control.is_in_valid_state(STANDBY_INFO, "State")

        LOGGER.info("Tear Down complete. Telescope is in Standby State")

    elif subarray_node_obsstate in ["ABORTED", "FAULT"]:
        tmc_helper.invoke_restart(**kwargs)
        LOGGER.info("Invoking Restart command on TMC SubarrayNode")
        assert telescope_control.is_in_valid_state(EMPTY_INFO, "obsState")

        tmc_helper.set_to_standby(**kwargs)
        LOGGER.info("Invoking Standby command on TMC SubarrayNode")
        assert telescope_control.is_in_valid_state(STANDBY_INFO, "State")

        LOGGER.info("Tear Down complete. Telescope is in Standby State")

    for device in DEVICE_LIST:
        device_proxy = DeviceProxy(device)
        device_proxy.ClearCommandCallInfo()

    LOGGER.info("Tear Down Successful, raising an exception for failure")
    if raise_exception:
        # pylint: disable=broad-exception-raised
        raise Exception(
            f"Test case failed and Subarray obsState was: "
            f"{subarray_node_obsstate}"
        )


def tear_down_configured_alarms(
    alarm_handler_device: DeviceProxy, alarms_to_remove: list
):
    """
    A method to remove configured alarms using the tag
    Arg:
        alarm_handler_device(DeviceProxy): device proxy for
        alarm handler device
        alarms_to_remove(list): list of alarms to remove
    """
    for tag in alarms_to_remove:
        alarm_handler_device.Remove(tag)
    assert alarm_handler_device.alarmList == ()


def prepare_json_args_for_commands(
    args_for_command: str, command_input_factory: JsonFactory
) -> str:
    """This method return input json based on command args"""
    if args_for_command is not None:
        input_json = command_input_factory.create_subarray_configuration(
            args_for_command
        )
    else:
        input_json = None
    return input_json


def prepare_json_args_for_centralnode_commands(
    args_for_command: str, command_input_factory: JsonFactory
) -> str:
    """This method return input json based on command args"""
    if args_for_command is not None:
        input_json = command_input_factory.create_centralnode_configuration(
            args_for_command
        )
    else:
        input_json = None
    return input_json


def set_subarray_to_given_obs_state(
    central_node,
    subarray_node,
    obs_state: str,
    event_tracer,
    command_input_factory,
):
    """Set the Subarray node to given obsState."""
    # This method with be removed after the helper devices are updated to have
    # a ThreadPoolExecutor.
    match obs_state:
        case "RESOURCING":
            # Setting the device defective
            csp_subarray = DeviceProxy(csp_subarray1_low)
            csp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

            subarray_node.force_change_of_obs_state(obs_state)

            # Waiting for SDP Subarray to go to ObsState.IDLE
            sdp_subarray = DeviceProxy(sdp_subarray1_low)
            event_tracer.subscribe_event(sdp_subarray, "obsState")

            assert_that(event_tracer).described_as(
                'FAILED ASSUMPTION IN "GIVEN STEP: '
                f'"a Subarray in intermediate obsState {obs_state}"'
                "SDP Subarray device"
                f"({sdp_subarray.dev_name()}) "
                f"is expected to be in IDLE obstate",
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                sdp_subarray,
                "obsState",
                ObsState.IDLE,
            )

            # Resetting defect on CSP Subarray.
            csp_subarray.SetDefective(json.dumps({"enabled": False}))
            start_time = time.time()
            while json.loads(csp_subarray.defective)["enabled"]:
                elapsed_time = time.time() - start_time
                if elapsed_time > TIMEOUT:
                    LOGGER.error("Failed to reset defective")
                    raise AssertionError("defective is not False")

        case "CONFIGURING":
            assign_input_str = prepare_json_args_for_commands(
                "assign_resources_low", command_input_factory
            )
            central_node.store_resources(assign_input_str)

            assert_that(event_tracer).described_as(
                'FAILED ASSUMPTION IN "GIVEN STEP: '
                f'"a Subarray in intermediate obsState {obs_state}"'
                "SDP Subarray device"
                f"({central_node.subarray_node.dev_name()}) "
                f"is expected to be in IDLE obstate",
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                central_node.subarray_node,
                "obsState",
                ObsState.IDLE,
            )
            # Setting the device defective
            csp_subarray = DeviceProxy(csp_subarray1_low)
            csp_subarray.SetDefective(
                json.dumps(INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT)
            )

            configure_input = prepare_json_args_for_commands(
                "configure_low", command_input_factory
            )
            subarray_node.execute_transition("Configure", configure_input)

            # Waiting for SDP Subarray to go to ObsState.READY
            sdp_subarray = DeviceProxy(sdp_subarray1_low)
            event_tracer.subscribe_event(sdp_subarray, "obsState")
            assert_that(event_tracer).described_as(
                'FAILED ASSUMPTION IN "GIVEN STEP: '
                f'"a Subarray in intermediate obsState {obs_state}"'
                "SDP Subarray device"
                f"({sdp_subarray.dev_name()}) "
                f"is expected to be in READY obstate",
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                sdp_subarray,
                "obsState",
                ObsState.READY,
            )
            # Resetting defect on CSP Subarray.
            csp_subarray.SetDefective(json.dumps({"enabled": False}))
