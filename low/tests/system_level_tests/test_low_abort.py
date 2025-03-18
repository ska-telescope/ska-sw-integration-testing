import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
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


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_xxxx_abort.feature",
    " TMC validates Abort Command",
)
def test_telescope_abort():
    """
    Test case to verify Abort functionality
    """


#  @given("telescope is in ON state") -> conftest


@given(parsers.parse("subarray is in IDLE ObsState"))
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


@when("I Abort it")
def invoke_end(
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Invokes ABORT command"""
    _, pytest.unique_id = subarray_node_low.abort_subarray()


@then("the TMC, CSP, SDP and MCCS subarrays transition to ABORTED obsState")
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
