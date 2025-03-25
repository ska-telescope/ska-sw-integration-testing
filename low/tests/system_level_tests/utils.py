import json
import logging

import pytest
from assertpy import assert_that
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer
from tango import DeviceProxy
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import update_eb_pb_ids
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])
configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def subscribe_to_obsstate_events(
    event_tracer, subarray_devices, subarray_node
):
    """Subscribe to obsState events for all relevant subarray devices."""
    event_tracer.subscribe_event(subarray_devices["sdp_subarray"], "obsState")
    event_tracer.subscribe_event(subarray_devices["csp_subarray"], "obsState")
    event_tracer.subscribe_event(subarray_devices["mccs_subarray"], "obsState")
    event_tracer.subscribe_event(subarray_node, "obsState")


def check_subarray_obsstate(
    subarray_devices: dict,
    subarray_node,
    event_tracer: TangoEventTracer,
    obs_state: ObsState,
):
    """Check if each subarray device is in the expected obsState."""
    subarray_devices = {
        "SDP": subarray_devices["sdp_subarray"],
        "CSP": subarray_devices["csp_subarray"],
        "MCCS": subarray_devices["mccs_subarray"],
        "TMC": subarray_node,
    }

    for name, device in subarray_devices.items():
        assert_that(event_tracer).described_as(
            f"{name} Subarray device ({device.dev_name()}) "
            f"should be in {obs_state.name} obsState."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            device, "obsState", obs_state
        )


def set_subarray_to_idle(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
    subarray_id: str,
):
    """Helper method to set subarray to IDLE ObsState."""
    # Subscribe to obsState change events
    json = ""
    if subarray_id == "1":
        json = "assign_resources_low_real_subarray1_station1"
        # json = "assign_resources_low_real"
        LOGGER.info("Subarray Id 1")
    elif subarray_id == "2":
        subarray_node_low = SubarrayNodeWrapperLow("2")
        json = "assign_resources_low_real_subarray2_station2"
        LOGGER.info("Subarray Id 2")
    else:
        LOGGER.info("Invalid Subarray Id")

    LOGGER.info(
        "subarray_node_low.subarray_devices: %s",
        subarray_node_low.subarray_devices,
    )
    LOGGER.info(
        "subarray_node_low.subarray_node: %s", subarray_node_low.subarray_node
    )
    subscribe_to_obsstate_events(
        event_tracer,
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
    )

    cbf_proc1 = DeviceProxy("low-cbf/processor/0.0.0")
    cbf_proc2 = DeviceProxy("low-cbf/processor/0.0.1")

    cbf_proc1.serialnumber = "XFL14SLO1LIF"
    cbf_proc1.subscribetoallocator("low-cbf/allocator/0")
    cbf_proc1.register()

    cbf_proc2.serialnumber = "XFL1HOOQ1Y44"
    cbf_proc2.subscribetoallocator("low-cbf/allocator/0")
    cbf_proc2.register()
    # Prepare and assign resources
    input_json = prepare_json_args_for_centralnode_commands(
        json, command_input_factory
    )
    assign_input_json = update_eb_pb_ids(input_json)
    # central_node_low.set_serial_number_of_cbf_processor()
    _, unique_id = central_node_low.store_resources(
        assign_input_json, subarray_id
    )

    # Verify longRunningCommandResult for the TMC Central Node
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )

    # Confirm subarray is in IDLE ObsState
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.IDLE,
    )


def execute_command(
    subarray_node_low,
    event_tracer,
    command_name,
    command_input_factory=None,
    expected_obs_state=None,
    timeout=TIMEOUT,
):
    """
    Helper function to execute a command on subarray node and verify obsState.
    """
    if command_name.lower() == "configure":
        input_json = prepare_json_args_for_commands(
            "configure_low_real", command_input_factory
        )
        _, pytest.unique_id = subarray_node_low.store_configuration_data(
            input_json, "1"
        )
    else:
        subarray_node_low.execute_transition(command_name)

    # Verify if the command was successful
    if expected_obs_state:
        assert_that(event_tracer).described_as(
            f"FAILED ASSUMPTION: Subarray is not in the expected "
            f"obsState '{expected_obs_state}'"
        ).within_timeout(timeout).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (pytest.unique_id[0], COMMAND_COMPLETED),
        )
        check_subarray_obsstate(
            subarray_node_low.subarray_devices,
            subarray_node_low.subarray_node,
            event_tracer,
            obs_state=expected_obs_state,
        )


def set_subarray_to_ready(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Helper method to set subarray to READY ObsState using
    execute_command."""
    execute_command(
        subarray_node_low=subarray_node_low,
        event_tracer=event_tracer,
        command_name="configure",
        command_input_factory=command_input_factory,
        expected_obs_state=ObsState.READY,
    )
