import json

import pytest
from assertpy import assert_that
from pytest_bdd import parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    set_subarray_to_idle,
    subscribe_to_obsstate_events,
)

TIMEOUT = 100


@pytest.mark.test1
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_xxxx_abort.feature",
    "TMC validates Abort Command",
)
def test_telescope_abort():
    """
    Test case to verify Abort functionality
    """


#  @given("telescope is in ON state") -> conftest


@then(parsers.parse("subarrays is in IDLE ObsState"))
def subarray_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    subscribe_to_obsstate_events(event_tracer, subarray_node_low)
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
    )


# @then(parsers.parse("subarrays is in READY ObsState"))
# def subarray_in_ready_obsstate(
#     subarray_node_low: SubarrayNodeWrapperLow,
#     command_input_factory,
#     event_tracer: TangoEventTracer,
# ):
#     subscribe_to_obsstate_events(event_tracer, subarray_node_low)
#     set_subarray_to_ready(
#         subarray_node_low,
#         command_input_factory,
#         event_tracer,
#     )


# @then(parsers.parse("subarrays is in SCANNING ObsState"))
# def subarray_in_scanning_obsstate(
#     subarray_node_low: SubarrayNodeWrapperLow,
#     command_input_factory,
#     event_tracer: TangoEventTracer,
# ):
#     subscribe_to_obsstate_events(event_tracer, subarray_node_low)
#     set_subarray_to_scanning(
#         subarray_node_low,
#         command_input_factory,
#         event_tracer,
#     )


# @then(parsers.parse("subarrays is in RESOURCING ObsState"))
# def subsystem_subarrays_in_resourcing(
#     subarray_node_low: SubarrayNodeWrapperLow,
#     event_tracer: TangoEventTracer,
# ):
#     """Check if all subarrays are in RESOURCING obsState."""
#     check_subarray_obsstate(
#         subarray_node_low,
#         event_tracer,
#         obs_state=ObsState.RESOURCING,
#     )


# @then("subarrays is in CONFIGURING obsState")
# def subsystem_subarrays_in_configuring(
#     subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
# ):
#     """Check if all subarrays are in CONFIGURING obsState."""
#     # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
#     # observation state by verifying the observed state changes for each
#     # subarray device. This function can be used to validate any obsState.
#     check_subarray_obsstate(
#         subarray_node_low,
#         event_tracer,
#         obs_state=ObsState.CONFIGURING,
#     )


@when("I Abort it")
def invoke_end(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Invokes ABORT command"""
    _, unique_id = subarray_node_low.abort_subarray()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.STARTED,"Command Started"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.STARTED), "Command Started")),
        ),
    )


@then("the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState")
def subsystem_subarrays_in_idle(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Check if all subarrays are in IDLE obsState."""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device. This function can be used to validate any obsState.
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.ABORTED,
    )
