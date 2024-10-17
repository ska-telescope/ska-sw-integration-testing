"""Test module to test TMC-CSP End functionality."""
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)

LOGGER = logging.getLogger(__name__)


@pytest.mark.skip
@pytest.mark.tmc_csp
@scenario(
    "../../mid/features/tmc_csp/xtp_29394_endscan.feature",
    "TMC executes a EndScan command on CSP subarray.",
)
def test_tmc_csp_endscan_functionality():
    """
    Test case to verify TMC-CSP observation End functionality
    """


@given(parsers.parse("TMC subarray {subarray_id} is in Scanning ObsState"))
def move_subarray_node_to_scanning_obsstate(
    central_node_mid, event_recorder, command_input_factory, subarray_node
):
    """Method to check tmc and csp subarray is in READY obstate"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    # execute set of commands and bring SubarrayNode to SCANNING obsState
    subarray_node.force_change_of_obs_state(
        "SCANNING",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )


@when(
    parsers.parse(
        "I issue the Endscan command to the TMC subarray {subarray_id}"
    )
)
def invoke_endscan_command(subarray_node):
    """Invoke Endscan command."""
    subarray_node.remove_scan_data()


@then(parsers.parse("the CSP subarray transitions to ObsState READY"))
def check_if_csp_subarray_moved_to_idle_obsstate(
    event_recorder, subarray_node
):
    """check CSP subarray obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState READY"
    )
)
def check_if_tmc_subarray_moved_to_ready_obsstate(
    event_recorder, subarray_node
):
    """Ensure TMC Subarray is moved to READY obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
