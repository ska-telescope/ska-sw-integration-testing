"""Module for TMC-CSP Abort command tests"""

import json

import pytest
from pytest_bdd import given, scenario, then
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import set_receive_address
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-30154_abort_in_configuring.feature",
    "Abort configuring CSP using TMC",
)
def test_abort_in_configuring():
    """BDD test scenario for verifying successful execution of
    the Abort command in Configuring state with TMC and CSP devices for
    pairwise testing."""


@given("TMC and CSP subarray busy configuring")
def subarray_busy_configuring(
    central_node_low,
    subarray_node_low,
    event_recorder,
    command_input_factory,
):
    """Subarray busy Configuring"""
    # Turning the devices ON
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
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
    _, unique_id = central_node_low.store_resources(input_json)
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )

    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    # Invoking Configure command
    subarray_node_low.store_configuration_data(configure_input_json)

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
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
