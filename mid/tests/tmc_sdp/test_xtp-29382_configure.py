"""Test module for TMC-SDP Configure functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.skip
@pytest.mark.tmc_sdp
@scenario(
    "../../mid/features/tmc_sdp/xtp-29382_configure.feature",
    "Configure a SDP subarray for a scan using TMC",
)
def test_tmc_sdp_configure():
    """
    Test case to verify TMC-SDP Configure functionality

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
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


@given(parsers.parse("TMC subarray in obsState IDLE"))
def check_subarray_obs_state(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """Method to check subarrays is in IDLE obsstate"""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.RESOURCING,
    )
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


@when(
    parsers.parse("I configure with {scan_type} to the subarray {subarray_id}")
)
def invoke_configure(
    central_node_mid,
    subarray_node,
    scan_type,
    subarray_id,
    command_input_factory,
):
    """A method to invoke Configure command"""
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    input_json = json.loads(input_json)
    input_json["sdp"]["scan_type"] = scan_type
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.store_configuration_data(json.dumps(input_json))


@then(parsers.parse("the SDP subarray {subarray_id} obsState is READY"))
def check_sdp_subarray_in_ready(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "SDP subarray scanType reflects correctly configured {scan_type}"
    )
)
def check_sdp_subarray_scan_type(subarray_node, event_recorder, scan_type):
    """A method to check SDP subarray obsstates"""
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "scanType"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"], "scanType", scan_type
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState is transitioned to READY"
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
