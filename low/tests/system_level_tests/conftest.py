import json

import pytest
from assertpy import assert_that
from pytest_bdd import given
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DeviceProxy, DevState
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


@given("a Low telescope")
def given_the_sut(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
) -> None:
    """
    Given a TMC

    Args:
        central_node_low: fixture for a TMC CentralNode under test
        subarray_node_low: fixture for a TMC SubarrayNode under test
        event_tracer: fixture for EventTracer class
    """

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert subarray_node_low.subarray_devices["sdp_subarray"].ping() > 0
    event_tracer.subscribe_event(central_node_low.csp_master, "State")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "State"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "State"
    )
    event_tracer.subscribe_event(central_node_low.sdp_master, "State")
    event_tracer.subscribe_event(central_node_low.mccs_master, "State")
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanID"
    )
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            subarray_node_low.subarray_node: ["longRunningCommandResult"],
            subarray_node_low.subarray_devices["csp_subarray"]: ["State"],
            subarray_node_low.subarray_devices["sdp_subarray"]: [
                "State",
                "scanID",
            ],
            subarray_node_low.subarray_devices["mccs_subarray"]: ["State"],
            central_node_low.sdp_master: ["State"],
            central_node_low.csp_master: ["State"],
            central_node_low.mccs_master: ["State"],
        }
    )


def check_devices_state_on(
    event_tracer: TangoEventTracer,
    devices: dict,
    expected_state: DevState = DevState.ON,
):
    """Helper function to check if multiple devices are in the
    expected state."""
    for name, device in devices.items():
        assert_that(event_tracer).described_as(
            f"FAILED ASSUMPTION AFTER ON COMMAND: "
            f"{name} device ({device.dev_name()}) "
            f"is expected to be in State {expected_state.name}"
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            device, "State", expected_state
        )


@given("a Telescope consisting of SDP, CSP and MCCS that is ON")
@given("telescope is in ON state")
def check_state_is_on(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """A method to check CentralNode.telescopeState"""
    central_node_low.move_to_on()

    devices = {
        "CSP Master": central_node_low.csp_master,
        "CSP Subarray": subarray_node_low.subarray_devices["csp_subarray"],
        "SDP Master": central_node_low.sdp_master,
        "SDP Subarray": subarray_node_low.subarray_devices["sdp_subarray"],
        "MCCS Master": central_node_low.mccs_master,
        "MCCS Subarray": subarray_node_low.subarray_devices["mccs_subarray"],
    }

    # Check if all devices are in ON state
    check_devices_state_on(event_tracer, devices)

    # Check if the Central Node is in TelescopeState ON
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node, "telescopeState", DevState.ON
    )


def subscribe_to_obsstate_events(event_tracer, subarray_node_low):
    """Subscribe to obsState events for all relevant subarray devices."""
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")


def check_subarray_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obs_state: ObsState,
):
    """Check if each subarray device is in the expected obsState."""
    subarray_devices = {
        "SDP": subarray_node_low.subarray_devices["sdp_subarray"],
        "CSP": subarray_node_low.subarray_devices["csp_subarray"],
        "MCCS": subarray_node_low.subarray_devices["mccs_subarray"],
        "TMC": subarray_node_low.subarray_node,
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
):
    """Helper method to set subarray to IDLE ObsState."""
    # Subscribe to obsState change events
    subscribe_to_obsstate_events(event_tracer, subarray_node_low)
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
        "assign_resources_low_real", command_input_factory
    )
    assign_input_json = update_eb_pb_ids(input_json)
    # central_node_low.set_serial_number_of_cbf_processor()
    _, unique_id = central_node_low.store_resources(assign_input_json)

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
        subarray_node_low, event_tracer, obs_state=ObsState.IDLE
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
            "configure_low", command_input_factory
        )
        _, pytest.unique_id = subarray_node_low.store_configuration_data(
            input_json
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
            subarray_node_low, event_tracer, obs_state=expected_obs_state
        )


def set_subarray_to_ready(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Helper method to set subarray to READY ObsState."""
    # Configure the subarray for a scan
    configure_input_json = prepare_json_args_for_commands(
        "configure_low_real", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )

    # Verify longRunningCommandResult for the TMC Subarray Node
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )

    # Confirm subarray is in READY ObsState
    check_subarray_obsstate(
        subarray_node_low, event_tracer, obs_state=ObsState.READY
    )
