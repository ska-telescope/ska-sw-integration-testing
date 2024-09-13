"""Test module to test TMC-CSP EndScan functionality."""

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-30014_end_scan_csp.feature",
    "TMC executes a EndScan command on CSP subarray",
)
def test_tmc_csp_endscan_functionality():
    """BDD test scenario for verifying successful execution of
    the EndScan command with TMC and CSP devices for pairwise
    testing.
    """


@given("the telescope is in ON state")
def given_a_telescope_on_state(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Ensure that the telescope is in the ON state for the test.

    Args:
        central_node_low (CentralNodeWrapperLow): Fixture for TMC CentralNode.
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        event_recorder (EventRecorder): Fixture for recording events.

    Raises:
        AssertionError: If the telescope is not in the ON state.
    """
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("TMC subarray {subarray_id} is in SCANNING obsState"))
def move_subarray_node_to_scanning_obsstate(
    central_node_real_csp_low,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Move TMC Subarray to the SCANNING obsstate.

    Args:
        central_node_low (CentralNodeWrapperLow): Fixture for TMC CentralNode.
        event_recorder (EventRecorder): Fixture for recording events.
        command_input_factory (JsonFactory): Factory for creating JSON input.
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        subarray_id (str): Identifier for the TMC subarray.

    Raises:
        AssertionError: If the subarray is not in the READY ObsState.
    """

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    central_node_real_csp_low.set_serial_number_of_cbf_processor()

    # execute set of commands and bring SubarrayNode to SCANNING obsState
    subarray_node_low.force_change_of_obs_state(
        "SCANNING",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
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


@when("I issue the Endscan command to the TMC subarray")
def invoke_endscan_command(subarray_node_low: SubarrayNodeWrapperLow):
    """Invoke the EndScan command on TMC.

    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
    """
    subarray_node_low.remove_scan_data()


@then("the CSP subarray transitions to obsState READY")
def check_if_csp_subarray_moved_to_idle_obsstate(
    event_recorder: EventRecorder, subarray_node_low: SubarrayNodeWrapperLow
):
    """Check if the CSP Subarray's obsState transitions to READY.

    Args:
        subarray_node_low (CentralNodeWrapperLow): Fixture for TMC CentralNode.
        event_recorder (EventRecorder): Fixture for recording events.

    Raises:
        AssertionError: If the CSP subarray obsState does not transition to
        SCANNING.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=10,
    )


@then("the TMC subarray transitions to obsState READY")
def check_if_tmc_subarray_moved_to_ready_obsstate(
    event_recorder: EventRecorder, subarray_node_low: SubarrayNodeWrapperLow
):
    """Check if the TMC Subarray's obsState transitions back to READY.

    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        event_recorder (EventRecorder): Fixture for recording events.

    Raises:
        AssertionError: If the TMC subarray obsState does not transition back
          to READY.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
