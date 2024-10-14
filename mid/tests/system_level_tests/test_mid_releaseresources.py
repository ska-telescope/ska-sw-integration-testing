"""Test module for ReleaseResources functionality (XTP-67033)"""
import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.sdp_facade import (
    SDPFacade,  # SDP facade
)
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer
from tests.system_level_tests.conftest import (
    SubarrayTestContextData,
    _setup_event_subscriptions,
    verify_subarrays_transition,
)
from tests.system_level_tests.utils.my_file_json_input import MyFileJSONInput

TIMEOUT = 100


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/xtp_65630_assign_release.feature",
    "Release resources from Mid subarray",
)
def test_telescope_release_resources():
    """BDD test scenario for verifying successful execution of
    the ReleaseResources command with TMC,CSP and SDP
    devices for pairwise testing"""


#  @given("telescope is in ON state") -> conftest


@given("subarray is in the IDLE obsState")
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    central_node_facade: TMCCentralNodeFacade,
    default_commands_inputs: TestHarnessInputs,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Ensure the subarray is in the IDLE state."""
    _setup_event_subscriptions(
        central_node_facade, subarray_node_facade, csp, sdp, event_tracer
    )
    context_fixt.starting_state = ObsState.IDLE

    subarray_node_facade.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )


@when("I release all resources assigned to it")
def invoke_releaseresources(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):
    """
    Send the ReleaseResources command to the subarray.
    """
    context_fixt.when_action_name = "ReleaseResources"

    json_input = MyFileJSONInput(
        "centralnode", "release_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.release_resources(
        json_input,
        wait_termination=False,
    )


@then("the TMC, CSP and SDP subarrays transition to RESOURCING obsState")
def verify_resourcing_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the RESOURCING state.
    """
    verify_subarrays_transition(
        event_tracer,
        context_fixt,
        ObsState.RESOURCING,
        subarray_node_facade.subarray_node,
        csp.csp_subarray,
        sdp.sdp_subarray,
    )

    # Override the starting state for the next step
    context_fixt.starting_state = ObsState.RESOURCING


@then("the TMC, CSP and SDP subarrays must be in EMPTY obsState")
def verify_empty_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the RESOURCING state.
    """
    verify_subarrays_transition(
        event_tracer,
        context_fixt,
        ObsState.EMPTY,
        subarray_node_facade.subarray_node,
        csp.csp_subarray,
        sdp.sdp_subarray,
    )
