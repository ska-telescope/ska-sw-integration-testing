"""Test module for TMC-SDP EndScan functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from Mid.tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from Mid.tests.resources.test_harness.utils.common_utils import (
    wait_added_for_skb372,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29385_end_scan.feature",
    "TMC executes a EndScan command on SDP subarray",
)
def test_tmc_sdp_endscan():
    """
    Test case to verify TMC-SDP EndScan functionality

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
        - "subarray_node": fixture for a TMC SubarrayNode under test
    """


@given("the telescope is in ON state")
def given_a_tmc(subarray_node, central_node_mid, event_recorder):
    """
    Given a TMC
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "State"
    )

    if central_node_mid.telescope_state != "ON":
        central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("TMC subarray {subarray_id} is in Scanning ObsState"))
def check_subarray_is_configured(
    central_node_mid,
    subarray_node,
    command_input_factory,
    event_recorder,
    subarray_id,
):
    """Method to check TMC and SDP subarrays in SCANNING obsstate"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_json = json.loads(configure_input_json)
    configure_json["tmc"]["scan_duration"] = 10.0
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )

    central_node_mid.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    wait_added_for_skb372()
    subarray_node.store_configuration_data(json.dumps(configure_json))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    subarray_node.store_scan_data(scan_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
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
def invoke_scan(central_node_mid, subarray_node, subarray_id):
    """A method to invoke EndScan command"""
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("EndScan")


@then(parsers.parse("the SDP subarray transitions to ObsState READY"))
def check_sdp_subarray_in_ready(subarray_node, event_recorder):
    """A method to check SDP subarray obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState READY"
    )
)
def check_tmc_subarray_obs_state(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check TMC subarray obsstate"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
