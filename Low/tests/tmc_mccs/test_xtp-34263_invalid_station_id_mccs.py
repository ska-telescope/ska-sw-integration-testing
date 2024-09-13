"""Test module for TMC-MCCS handle invalid json(invalid station id)"""
# import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

# from tests.resources.test_harness.constant import (
#     mccs_master_leaf_node,
#     tmc_low_subarraynode1,
# )
from tests.resources.test_harness.helpers import updated_assign_str
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_mccs1
@scenario(
    "../features/tmc_mccs/xtp-34263_invalid_json_mccs.feature",
    "The TMC Low Subarray reports the exception triggered by the MCCS "
    + "controller when it encounters an invalid station ID.",
)
def test_invalid_station_id_reporting_tmc_mccs_controller():
    """
    Test the behavior of the MCCS controller when an invalid station ID is
      provided.

    This test case checks that the MCCS controller correctly reports the error
      for an invalid station ID and that the system transitions to the expected
            states after the error occurs.

    """


@given("a Telescope consisting of TMC-MCCS, emulated SDP and emulated CSP")
def given_telescope_setup_with_simulators(central_node_low, simulator_factory):
    """
    Given a Telescope setup including TMC-MCCS, emulated SDP, and emulated CSP.
    Checks if all necessary simulator devices are reachable.
    """
    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_MASTER_DEVICE
    )
    assert csp_master_sim.ping() > 0
    assert sdp_master_sim.ping() > 0
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given("the Telescope is in the ON state")
def check_telescope_is_in_on_state(central_node_low, event_recorder) -> None:
    """
    Ensure the Telescope is in the ON state and subscribe to the telescopeState
    event.
    """
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the TMC subarray is in EMPTY obsState")
def tmc_subarray_in_empty_obsstate(subarray_node_low, event_recorder):
    """
    Check if the TMC subarray's obsState attribute value is EMPTY
    and subscribe to the obsState event.
    """
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.EMPTY
    )


@when(
    parsers.parse(
        "I assign resources with invalid {station_id} "
        + "to the MCCS subarray using TMC with {subarray_id}"
    )
)
def invoke_assignresources(
    station_id: int,
    central_node_low,
    command_input_factory,
    subarray_id,
    stored_unique_id,
):
    """
    Invoke AssignResources command on TMC with invalid station_id to the MCCS
    subarray.
    """
    central_node_low.set_subarray_id(subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_json_string = updated_assign_str(
        input_json,
        int(station_id),
    )
    _, unique_id = central_node_low.perform_action(
        "AssignResources", assign_json_string
    )
    stored_unique_id.append(unique_id[0])


@then("the MCCS controller rejects invalid station id")
def invalid_command_rejection(
    event_recorder, central_node_low, stored_unique_id
):
    """
    Ensure that the MCCS controller throws an error for the invalid station ID
    and subscribe to the longRunningCommandResult event.
    """
    event_recorder.subscribe_event(
        central_node_low.mccs_master_leaf_node,
        "longRunningCommandResult",
    )

    assert stored_unique_id[0].endswith("AssignResources")

    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.mccs_master_leaf_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(
            Anything,
            "3",
        ),
    )
    # Extract the actual message from the assertion data
    actual_attribute_value = assertion_data["attribute_value"]

    assert "AssignResources" in actual_attribute_value[0]
    assert ResultCode(int(actual_attribute_value[1])) == ResultCode.FAILED


@then("the MCCS subarray should remain in EMPTY ObsState")
def mccs_subarray_remains_in_empty_obsstate(event_recorder, subarray_node_low):
    """
    Check that the MCCS subarray remains in the EMPTY obsState.
    """
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.EMPTY,
    )


@then("the TMC propogate the error to the client")
def central_node_receiving_error(
    event_recorder, central_node_low, stored_unique_id
):
    """
    Ensure that the TMC propagates the error to the client and subscribe to
    the longRunningCommandResult event.
    """
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult", timeout=80.0
    )
    expected_long_running_command_result = (
        stored_unique_id[0],
        "Exception occurred on the following devices"
        ": ska_low/tm_leaf_node/mccs_master: Timeout has occurred, "
        "command failedska_low/tm_subarray_node/1: "
        "Timeout has occurred, command failed",
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        expected_long_running_command_result,
        lookahead=10,
    )


@then("the TMC SubarrayNode remains in RESOURCING obsState")
def tmc_subarray_remains_in_resourcing_obsstate(
    event_recorder, subarray_node_low
):
    """
    Check that the TMC SubarrayNode remains in the RESOURCING obsState
    and subscribe to the obsState event.
    """
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
