import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.sdp_facade import (
    SDPFacade,  # CSP facade
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
from tests.system_level_tests.conftest import SubarrayTestContextData
from tests.system_level_tests.utils.my_file_json_input import MyFileJSONInput

TIMEOUT = 60


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/xtp_xxxxx_assign_release.feature",
    "Release resources from mid Subarray",
)
def test_releaseresources_command():
    """BDD test scenario for verifying successful execution of
    the ReleaseResources command with TMC,CSP and SDP devices for pairwise
    testing."""


@given("I invoke the ON command on the telescope")
def send_telescope_on_command(
    event_tracer: TangoEventTracer, central_node_facade: TMCCentralNodeFacade
):
    """Send the TelescopeOn command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.move_to_on(wait_termination=False)


@given(parsers.parse("TMC subarray {subarray_id} is in IDLE ObsState"))
def subarray_in_idle_obsstate(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCSubarrayNodeFacade,
):

    context_fixt.starting_state = ObsState.IDLE

    central_node_facade.force_change_of_obs_state(
        ObsState.IDLE,
        TestHarnessInputs(),
        wait_termination=True,
    )


@when(
    parsers.parse("I release all resources with to TMC subarray {subarray_id}")
)
def invoke_releaseresources(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):
    """
    Send the ReleaseResources command to the subarray.

    This step uses the central_node_facade to send a ReleaseResources
    command to the specified subarray. It uses a pre-defined JSON input
    file, modifies the subarray_id, and sends the command without waiting
    for termination. The action result is stored in the context fixture.
    """
    context_fixt.when_action_name = "ReleaseResources"

    json_input = MyFileJSONInput(
        "centralnode", "release_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.release_resources(
        json_input,
        wait_termination=False,
    )


@then(
    parsers.parse(
        "the CSP,SDP and TMC subarray {subarray_id} must be in EMPTY ObsState"
    )
)
def csp_sdp_tmc_subarray_empty(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the EMPTY state.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
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
