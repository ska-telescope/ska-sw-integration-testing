"""Test module for ReleaseResources functionality (XTP-67033)"""
import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.sdp_facade import (
    SDPFacade,  # SDP facade
)
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer
from tests.system_level_tests.conftest import (
    SubarrayTestContextData,
    _setup_event_subscriptions,
)
from tests.system_level_tests.utils.json_file_input_handler import (
    MyFileJSONInput,
)

TIMEOUT = 100


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/"
    + "xtp_66801_telescope_observational_commands.feature",
    "Release resources from Mid subarray",
)
def test_telescope_release_resources():
    """BDD test scenario for verifying successful execution of
    the ReleaseResources command with TMC,CSP and SDP
    devices for pairwise testing"""


#  @given("telescope is in ON state") -> conftest


@when("I release all resources assigned to it")
def invoke_releaseresources(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Send the ReleaseResources command to the subarray.
    """
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    context_fixt.when_action_name = "ReleaseResources"

    json_input = MyFileJSONInput(
        "centralnode", "release_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = tmc.release_resources(
        json_input,
        wait_termination=False,
    )


@then("the TMC, CSP and SDP subarrays transition to EMPTY obsState")
def csp_sdp_tmc_subarray_empty(
    context_fixt,
    # subarray_id: str,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the EMPTY state.
    """
    assert_that(event_tracer).described_as(
        f"All three: TMC Subarray Node device "
        f"({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    )
