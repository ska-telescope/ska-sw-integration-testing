"""Test TMC-SDP Abort functionality in IDLE obstate"""
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.common_utils import (
    wait_added_for_skb372,
)


@pytest.mark.tmc_sdp
@scenario(
    "../../features/tmc_sdp/xtp_29397_abort_idle_ready.feature",
    "TMC executes an Abort on SDP subarray",
)
def test_tmc_sdp_abort_in_given_obsstate():
    """
    Test case to verify TMC-SDP Abort functionality in IDLE obsState
    """


@given("the telescope is in ON state")
def telescope_is_in_on_state(central_node_mid, event_recorder):
    """
    This method checks if the telescope is in ON state
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    logging.info(
        "Telescope State is: %s", central_node_mid.central_node.telescopeState
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.OFF,
    )
    logging.info(
        "Telescope State is: %s", central_node_mid.central_node.telescopeState
    )
    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    logging.info(
        "Telescope State is: %s", central_node_mid.central_node.telescopeState
    )


@given(
    parsers.parse(
        "TMC and SDP subarray {subarray_id} is in {obsstate} ObsState"
    )
)
def subarray_is_in_given_obsstate(
    central_node_mid,
    event_recorder,
    command_input_factory,
    obsstate,
    subarray_node,
    subarray_id,
):
    """ "A method to check if telescope in is given obsSstate."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.set_subarray_id(subarray_id)
    central_node_mid.store_resources(assign_input_json)
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    if obsstate == "READY":
        input_json = prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        )
        wait_added_for_skb372()
        subarray_node.store_configuration_data(input_json)
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "obsState",
            ObsState[obsstate],
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "obsState",
            ObsState[obsstate],
        )


@when(
    parsers.parse(
        "I issued the Abort command to the TMC subarray {subarray_id}"
    )
)
def invoke_abort(subarray_node, subarray_id):
    """
    This method invokes abort command on tmc subarray
    """
    subarray_node.set_subarray_id(subarray_id)
    subarray_node.abort_subarray()


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to ObsState ABORTED"
    )
)
def sdp_subarray_is_in_aborted_obsstate(
    subarray_node, event_recorder, subarray_id
):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState ABORTED"
    )
)
def tmc_subarray_is_in_aborted_obsstate(
    subarray_node, event_recorder, subarray_id
):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
