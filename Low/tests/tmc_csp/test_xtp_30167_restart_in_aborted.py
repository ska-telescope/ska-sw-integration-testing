"""Module for TMC-CSP Abort command tests"""

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-30167_restart_in_aborted.feature",
    "TMC executes a Restart on CSP subarray when subarray completes abort",
)
def test_restart_in_aborted():
    """BDD test scenario for verifying successful execution of
    the Restart command in Aborted state with TMC and CSP devices for pairwise
    testing."""


@given("the telescope is in ON state")
def telescope_in_on_state(central_node_real_csp_low, event_recorder):
    """On telescope"""
    central_node_real_csp_low.move_to_on()

    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(
    parsers.parse("TMC and CSP subarray {subarray_id} is in obsState ABORTED")
)
def subarray_in_aborted_state(
    subarray_node_real_csp_low, event_recorder, subarray_id
):
    """Subarray in Aborted state."""
    subarray_node_real_csp_low.set_subarray_id(subarray_id)
    subarray_node_real_csp_low.force_change_of_obs_state("ABORTED")

    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_node, "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@when("I command it to Restart")
def restart_subarray(subarray_node_real_csp_low):
    """Restart command invoked on Subarray Node"""
    subarray_node_real_csp_low.restart_subarray()


@then("the CSP subarray transitions to obsState EMPTY")
def csp_subarray_in_empty_obs_state(
    subarray_node_real_csp_low, event_recorder
):
    """CSP Subarray in EMPTY obsState."""
    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
        lookahead=10,
    )


@then("the TMC subarray transitions to obsState EMPTY")
def subarray_in_empty_obs_state(subarray_node_real_csp_low, event_recorder):
    """Subarray Node in EMPTY obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
        lookahead=10,
    )
    event_recorder.clear_events()
