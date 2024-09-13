"""Module for TMC-CSP Abort command tests"""
import pytest
from pytest_bdd import given, scenario, then
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import set_receive_address
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-30155_abort_in_scanning.feature",
    "Abort scanning CSP using TMC",
)
def test_abort_in_scanning():
    """BDD test scenario for verifying successful execution of
    the Abort command in Scanning state with TMC and CSP devices for pairwise
    testing."""


@given("TMC and CSP subarray busy scanning")
def subarray_busy_scanning(
    central_node_low,
    subarray_node_low,
    event_recorder,
    command_input_factory,
):
    """Subarray busy Scanning"""
    # Turning the devices ON
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    central_node_low.set_serial_number_of_cbf_processor()
    set_receive_address(central_node_low)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    # Invoking AssignResources command
    central_node_low.store_resources(input_json)
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    # Invoking Configure command
    subarray_node_low.store_configuration_data(configure_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    # Invoking Scan command
    subarray_node_low.store_scan_data(scan_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )


# @when -> ../conftest.py


@then("the CSP subarray should go into an aborted obsState")
def csp_subarray_in_aborted_obs_state(subarray_node_low, event_recorder):
    """CSP Subarray in ABORTED obsState."""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.ABORTED,
        lookahead=10,
    )


@then("the TMC subarray node obsState transitions to ABORTED")
def subarray_in_aborted_obs_state(subarray_node_low, event_recorder):
    """Subarray Node in ABORTED obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
        lookahead=10,
    )
    event_recorder.clear_events()
