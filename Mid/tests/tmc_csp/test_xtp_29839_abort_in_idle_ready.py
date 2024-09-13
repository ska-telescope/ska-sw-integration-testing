"""Test TMC-CSP Abort functionality in IDLE-READY obstate"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState

from Mid.tests.resources.test_harness.helpers import (
    get_master_device_simulators,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29839_abort_idle_ready.feature",
    "TMC executes an Abort on CSP subarray",
)
def test_tmc_csp_abort_in_given_obsstate(central_node_mid, simulator_factory):
    """
    Test case to verify TMC-CSP Abort functionality in IDLE-READY obsState
    """
    (
        csp_master_sim,
        _,
        _,
        _,
        _,
        _,
    ) = get_master_device_simulators(simulator_factory)

    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    assert csp_master_sim.ping() > 0


@given(
    parsers.parse(
        "the TMC subarray {subarray_id} and CSP subarray {subarray_id} are in "
        + "ObsState {obsstate}"
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
    """A method to check if telescope in is given obsSstate."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    subarray_node.set_subarray_id(subarray_id)
    central_node_mid.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    if obsstate == "READY":

        configure_json = prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        )
        subarray_node.store_configuration_data(configure_json)
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["csp_subarray"],
            "obsState",
            ObsState[obsstate],
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "obsState",
            ObsState[obsstate],
        )


@when("I issued the Abort command to the TMC subarray")
def invoke_abort(subarray_node):
    """
    This method invokes abort command on tmc subarray
    """
    subarray_node.abort_subarray()


@then("the CSP subarray transitions to ObsState ABORTED")
def csp_subarray_is_in_aborted_obsstate(subarray_node, event_recorder):
    """
    Method to check CSP subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then("the TMC subarray transitions to ObsState ABORTED")
def tmc_subarray_is_in_aborted_obsstate(subarray_node, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
