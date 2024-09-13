"""Module for TMC-CSP Abort command tests"""

import pytest
from pytest_bdd import given, parsers, scenario, then
from ska_control_model import ObsState
from tango import DevState


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-30156_abort_in_idle_ready.feature",
    "Abort resourced CSP and TMC subarray",
)
def test_abort_in_idle_ready():
    """BDD test scenario for verifying successful execution of
    the Abort command in Idle/Ready state with TMC and CSP devices for pairwise
    testing."""


@given(parsers.parse("TMC subarray in obsState {obsstate}"))
def subarray_in_given_obs_state(
    central_node_low,
    subarray_node_low,
    event_recorder,
    obsstate,
):
    """Subarray in given obsState"""
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

    # Using force change of obsState
    subarray_node_low.force_change_of_obs_state(obsstate)
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState[obsstate],
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
