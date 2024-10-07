"""Test module for AssignResources functionality (XTP-65635)"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)

TIMEOUT = 100


@pytest.mark.system_level_tests1
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_assign_release.feature",
    "Assign resources to low subarray",
)
def test_telescope_assign_resources():
    """
    Test case to verify AssignResources functionality
    """


#  @given("telescope is in ON state") -> conftest


@given("subarray is in EMPTY ObsState")
def subarray_in_empty_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder: TangoEventTracer,
    subarray_id: int = 1,
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    central_node_low.set_subarray_id(subarray_id)
    subscribe_to_obsstate_events(event_recorder, subarray_node_low)
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY


@when("I assign resources to the subarray")
def invoke_assignresources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Invokes AssignResources command on TMC"""
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.set_serial_number_of_cbf_processor()
    _, pytest.unique_id = central_node_low.store_resources(input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@then(
    "the TMC, CSP, SDP, and MCCS subarrays transition to RESOURCING obsState"
)
def subsystem_subarrays_in_resourcing(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obs_state: str,
):
    """Check if all subarrays are in RESOURCING obsState."""
    _check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.RESOURCING,
    )


@then("the TMC, CSP, SDP, and MCCS subarrays transition to IDLE obsState")
def subsystems_subarray_idle(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Check if all subarrays are in IDLE obsState."""
    _check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.IDLE,
    )


def subscribe_to_obsstate_events(event_tracer, subarray_node_low):
    """Subscribe to obsState events for all relevant subarray devices."""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.mccs_subarray_leaf_node, "obsState"
    )


def _check_subarray_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obs_state: ObsState,
):
    """Check if each subarray device is in the expected obsState."""
    subarray_devices = {
        "TMC": subarray_node_low.subarray_node,
        "SDP": subarray_node_low.sdp_subarray_leaf_node,
        "CSP": subarray_node_low.csp_subarray_leaf_node,
        "MCCS": subarray_node_low.mccs_subarray_leaf_node,
    }

    for name, device in subarray_devices.items():
        assert_that(event_tracer).described_as(
            f"{name} Subarray device ({device.dev_name()}) "
            f"should be in {obs_state.name} obsState."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            device, "obsState", obs_state
        )
