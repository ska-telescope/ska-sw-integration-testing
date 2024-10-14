"""Test module for AssignResources functionality (XTP-65630)"""
import pytest

# from assertpy import assert_that
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
    "Assign resources to Mid subarray",
)
def test_telescope_assign_resources():
    """BDD test scenario for verifying successful execution of
    the AssignResources command with TMC,CSP and SDP
    devices for pairwise testing"""


@given("subarray is in EMPTY ObsState")
def subarray_in_empty_obsstate(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    _setup_event_subscriptions(
        central_node_facade, subarray_node_facade, csp, sdp, event_tracer
    )
    context_fixt.starting_state = ObsState.EMPTY
    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        TestHarnessInputs(),
        wait_termination=True,
    )


@when("I assign resources to the subarray")
def invoke_assignresources(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):

    context_fixt.when_action_name = "AssignResources"
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
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


@then("the CSP, SDP and TMC subarrays must be in IDLE obsState")
def verify_idle_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the IDLE state.
    """
    verify_subarrays_transition(
        event_tracer,
        context_fixt,
        ObsState.IDLE,
        subarray_node_facade.subarray_node,
        csp.csp_subarray,
        sdp.sdp_subarray,
    )
