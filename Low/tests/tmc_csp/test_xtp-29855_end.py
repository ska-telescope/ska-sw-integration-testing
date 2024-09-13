"""Test module to test TMC-CSP End functionality."""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-29855_end.feature",
    "End Command to CSP subarray using TMC",
)
def test_tmc_csp_end_functionality(central_node_low) -> None:
    """
    Test case to verify TMC-CSP observation End functionality
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["csp_subarray"].ping() > 0


@given("the Telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_low, event_recorder: EventRecorder
) -> None:
    """Ensure telescope is in ON state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=15,
    )


@given(parsers.parse("a subarray {subarray_id} in the READY obsState"))
def move_subarray_node_to_ready_obsstate(
    central_node_real_csp_low,
    subarray_node_real_csp_low,
    event_recorder,
    command_input_factory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_node, "longRunningCommandResult"
    )
    central_node_real_csp_low.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_real_csp_low.set_serial_number_of_cbf_processor()

    _, unique_id = central_node_real_csp_low.store_resources(assign_input_json)

    event_recorder.subscribe_event(
        central_node_real_csp_low.subarray_node, "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_real_csp_low.store_configuration_data(
        configure_input_json
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@when("I issue End command to the subarray")
def invoke_end_command(subarray_node_low) -> None:
    """Invoke End command."""
    subarray_node_low.execute_transition("End")


@then("the CSP subarray transitions to IDLE obsState")
def check_if_csp_subarray_moved_to_idle_obsstate(
    subarray_node_low, event_recorder
):
    """Ensure CSP subarray is moved to IDLE obsstate"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then("TMC subarray transitions to IDLE obsState")
def check_if_tmc_subarray_moved_to_idle_obsstate(
    subarray_node_low, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to IDLE obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
