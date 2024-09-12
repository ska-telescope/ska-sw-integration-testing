"""Test module for TMC-SDP End functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29383_end.feature",
    "End configure from SDP Subarray using TMC",
)
def test_tmc_sdp_end():
    """
    Test case to verify TMC-SDP End functionality

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
        - "subarray_node": fixture for a TMC SubarrayNode under test
    """


@given("the Telescope is in ON state")
def given_a_tmc(central_node_mid, event_recorder):
    """
    Given a TMC
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    if central_node_mid.telescope_state != "ON":
        central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("a subarray {subarray_id} in the READY obsState"))
def check_subarray_obs_state(
    central_node_mid,
    subarray_node,
    command_input_factory,
    subarray_id,
    event_recorder,
):
    """Method to check subarray is in READY obstate"""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )

    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )

    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(parsers.parse("I issue End command to the subarray {subarray_id}"))
def invoke_end(central_node_mid, subarray_node, subarray_id):
    """A method to invoke End command"""
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("End")


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to IDLE obsState"
    )
)
def check_sdp_subarray_obs_state(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then(parsers.parse("TMC subarray {subarray_id} transitions to IDLE obsState"))
def check_tmc_subarray_obs_state(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check TMC subarray obsstate"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
