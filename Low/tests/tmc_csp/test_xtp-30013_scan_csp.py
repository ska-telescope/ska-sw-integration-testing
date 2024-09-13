"""Test module for TMC-CSP Scan functionality"""

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
    "../features/tmc_csp/xtp-30013_scan_csp.feature",
    "TMC executes a scan on CSP subarray",
)
def test_scan_command():
    """BDD test scenario for verifying successful execution of
    the Scan command with TMC and CSP devices for pairwise
    testing.
    """


@given("the Telescope is in ON state")
def given_a_telescope_in_on_state(
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
        subarray_node_low.subarray_devices["csp_subarray"], "State"
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


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def subarray_in_ready_obsstate(
    central_node_real_csp_low,
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to the READY obsstate.

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
    central_node_low.set_subarray_id(subarray_id)
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

    subarray_node_low.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )


@when("I issue scan command on subarray")
def invoke_scan(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
):
    """Invoke the Scan command on TMC.

    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        event_recorder (EventRecorder): Fixture for recording events.
        command_input_factory (JsonFactory): Factory for creating JSON input
    Raises:
        AssertionError: Scan Command is not Successful.
    """

    scan_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    subarray_node_low.store_scan_data(scan_json)


@then("the subarray obsState transitions to SCANNING")
def tmc_subarray_scanning(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Check if the SubarrayNode's obsState transitions to SCANNING.

    Args:
        central_node_low (CentralNodeWrapperLow): Fixture for TMC CentralNode.
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
        SubarrayNode.
        event_recorder (EventRecorder): Fixture for recording events.
        subarray_id (str): Identifier for the TMC subarray.

    Raises:
        AssertionError: If the obsState does not transition to SCANNING.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )


@then("the CSP subarray transitions to ObsState SCANNING")
def csp_subarray_scanning(
    subarray_node_low: SubarrayNodeWrapperLow, event_recorder: EventRecorder
):
    """Check if the CSP Subarray's obsState transitions to SCANNING.

    Args:
        subarray_node_low (CentralNodeWrapperLow): Fixture for TMC CentralNode.
        event_recorder (EventRecorder): Fixture for recording events.

    Raises:
        AssertionError: If the CSP subarray obsState does not transition
          to SCANNING.
    """
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )


@then(
    "the CSP subarray obsState transitions to READY "
    "after the scan duration elapsed"
)
def csp_subarray_obsState(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Checks if SubarrayNode's obsState attribute value is READY
    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        event_recorder (EventRecorder): Fixture for recording events.

    Raises:
        AssertionError: If the CSP subarray obsState does not transition
        back to READY.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=10,
    )


@then("the TMC subarray obsState transitions back to READY")
def tmc_subarray_ready(
    subarray_node_low: SubarrayNodeWrapperLow, event_recorder: EventRecorder
):
    """Check if the TMC Subarray's obsState transitions back to READY.

    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        event_recorder (EventRecorder): Fixture for recording events.

    Raises:
        AssertionError: If the TMC subarray obsState does not transition
        back to READY.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
