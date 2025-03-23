"""Test TMC-SDP Negative Scenarios Unavailable subsystem"""
import json
import os

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.control_model import HealthState
from ska_tango_testing.mock.placeholders import Anything
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    generate_eb_pb_ids,
    get_master_device_simulators,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper


@pytest.mark.skip(reason="This test case is not in the scope of this story")
@pytest.mark.tmc_sdp_unhappy
@scenario(
    "../../mid/features/tmc_sdp/xtp_39507_component_unavailable.feature",
    "SDP Subarray report the error when one of the SDP's component is"
    + " unavailable",
)
def test_sdp_component_unavailable(central_node_mid):
    """
    Test case to verify if one of the SDP component is unavailable
    """
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0


@given("a Telescope consisting of TMC,SDP,simulated CSP and simulated Dish")
def given_tmc_with_simulated_csp_dish(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    simulator_factory: SimulatorFactory,
):
    """A method to check if tmc subsystems are simulated."""

    assert os.environ.get("DISH_SIMULATION_ENABLED") == "true"
    assert os.environ.get("SDP_SIMULATION_ENABLED") == "false"
    assert os.environ.get("CSP_SIMULATION_ENABLED") == "true"
    (
        csp_master_sim,
        _,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_master_device_simulators(simulator_factory)
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    assert subarray_node.sdp_subarray_leaf_node.ping() > 0
    assert subarray_node.csp_subarray_leaf_node.ping() > 0
    assert csp_master_sim.ping() > 0
    assert dish_master_sim_1.ping() > 0
    assert dish_master_sim_2.ping() > 0
    assert dish_master_sim_3.ping() > 0
    assert dish_master_sim_4.ping() > 0


@given("the subarray is in EMPTY obsState")
def subarray_is_in_empty_obsstate(
    subarray_node,
    event_recorder,
):
    """A method to check if telescope in is EMPTY obsSstate."""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("one of the SDP's component subsystem is made unavailable")
def sdp_proc_controller_unavailable(central_node_mid: CentralNodeWrapperMid):
    """
    Processing controller is made unavailable in gitlab script, asserted SDP
    Controller's HealthState as degraded to verify the same
    """
    assert central_node_mid.sdp_master.healthState == HealthState.DEGRADED


@when(parsers.parse("I assign resources to the subarray {subarray_id}"))
def tmc_assign_resources_invoke(
    central_node_mid: CentralNodeWrapperMid,
    subarray_id: str,
    command_input_factory,
):
    """
    Method to invoke AssignResources command.
    """
    central_node_mid.set_subarray_id(subarray_id)
    assign_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    input_json = json.loads(assign_json)
    generate_eb_pb_ids(input_json)
    pytest.result, pytest.unique_id = central_node_mid.perform_action(
        "AssignResources", json.dumps(input_json)
    )


@then("SDP subarray report the unavailability of SDP Component")
def sdp_subarray_reports_unavailability(
    event_recorder: EventRecorder, central_node_mid: CentralNodeWrapperMid
):
    """
    Method to verify SDP subarray reports unavailability to TMC.
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node,
        "longRunningCommandResult",
    )
    exception_message = (
        "The processing controller, helm deployer, or both "
        + "are OFFLINE: cannot start processing blocks."
    )
    pytest.assertion_data = event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(pytest.unique_id[0], Anything),
    )
    assert "AssignResources" in pytest.assertion_data["attribute_value"][0]
    assert (
        exception_message
        in json.loads(pytest.assertion_data["attribute_value"][1])[1]
    )


@then("TMC should report the error to client")
def tmc_reports_unavailability_to_client(
    event_recorder: EventRecorder, central_node_mid: CentralNodeWrapperMid
):
    """
    Method to verify TMC subarray reports unavailability to client.
    """
    exception_message = (
        " mid-tmc/subarray/01 : Exception occurred on the"
        + " following devices: mid-tmc/subarray-leaf-node-sdp/01:"
        + " The processing controller, helm deployer, or both are OFFLINE:"
        + " cannot start processing blocks.\n"
    )
    assert "AssignResources" in pytest.assertion_data["attribute_value"][0]
    assert (
        exception_message
        in json.loads(pytest.assertion_data["attribute_value"][1])[1]
    )


@then(parsers.parse("the TMC SubarrayNode {subarray_id} stuck in RESOURCING"))
def tmc_stuck_in_resourcing(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
):
    """
    Method to verify the subarray stuck in RESOURCING obsstate
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    # Here the SDP is in EMPTY obsState and in decorators we are waiting for
    # all devices to be in ABORTED obsState, hence invoking Abort
    # command here only

    subarray_node.execute_transition(command_name="Abort", argin=None)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.ABORTED,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
