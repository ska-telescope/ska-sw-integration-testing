"""Test TMC-CSP Abort functionality in RESOURCING obsState"""


import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tests.resources.test_harness.helpers import (
    get_master_device_simulators,
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.skip(reason="Random failure")
# Random failure, SubarrayNode timed out, CORBA command timeout while
# invoking Abort command
# SubarrayNode receives obsstate IDLE event before Abort is successful on
# CspSuabrrayLeafNode and the tracker thread misbehaves, leading SA
# stuck in ABORTING
@pytest.mark.tmc_csp
@scenario(
    "../../features/tmc_csp/xtp_29840_abort_resourcing.feature",
    "Abort assigning CSP using TMC",
)
def test_tmc_csp_abort_in_resourcing(central_node_mid, simulator_factory):
    """
    Test case to verify TMC-CSP Abort functionality in RESOURCING obsState
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
        "the TMC subarray {subarray_id} and CSP subarray {subarray_id} are "
        + "busy in assigning"
    )
)
def subarray_is_in_resourcing_obsstate(
    central_node_mid,
    subarray_node,
    event_recorder,
    command_input_factory,
    subarray_id,
):
    """A method to check if telescope in is resourcing obsSstate."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    subarray_node.set_subarray_id(subarray_id)
    central_node_mid.perform_action("AssignResources", assign_input_json)

    event_recorder.subscribe_event(
        subarray_node.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.RESOURCING,
    )
    # Here the sleep is added to give time to subarraynode to
    # recieve and process obsState events from subsystem.
    time.sleep(1)


@when("I issued the Abort command to the TMC subarray")
def abort_is_invoked(subarray_node):
    """
    This method invokes abort command on tmc subarray.
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
