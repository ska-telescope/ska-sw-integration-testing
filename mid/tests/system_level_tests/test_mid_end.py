"""Test module for AssignResources functionality (XTP-65630)"""

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import (
    SDPFacade,  # SDP facade
)
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.inputs.pointing_state import PointingState
from ska_tango_testing.integration import TangoEventTracer
from tests.system_level_tests.conftest import (
    DISH_IDS,
    SubarrayTestContextData,
    _setup_event_subscriptions,
)
from tests.system_level_tests.utils.json_file_input_handler import (
    MyFileJSONInput,
)

TIMEOUT = 100


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/xtp_68817_configure_end.feature",
    "End command on Mid telescope",
)
def test_telescope_end_command():
    """BDD test scenario for verifying successful execution of
    the End command with TMC,CSP and SDP
    devices for pairwise testing"""


@given("subarray is in READY ObsState")
def set_subarray_to_ready(
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
    context_fixt.when_action_name = "AssignResources"
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
        json_input,
        wait_termination=False,
    )
    context_fixt.when_action_name = "Configure"

    json_input = MyFileJSONInput("subarray", "configure_mid")

    context_fixt.when_action_result = subarray_node_facade.configure(
        json_input,
        wait_termination=False,
    )
    assert_that(event_tracer).described_as(
        f"All three: TMC Subarray Node device "
        f"({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to READY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    )

    # override the starting state for the next step
    context_fixt.starting_state = ObsState.READY


@when("I issue the End command to subarray ")
def send_end_command(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Send the End command to the subarray.

    This step uses the subarray_node_facade to send an End command to the
    specified subarray. It sends the command without waiting for termination
    and stores the action result in the context fixture.
    """
    context_fixt.when_action_name = "End"

    context_fixt.when_action_result = subarray_node_facade.end_observation(
        wait_termination=False,
    )


@then(
    "the Telescope consisting of SDP and CSP devices transition to IDLE "
    "obsState"
)
def verify_idle_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that each sub system transitions to
    pointingState IDLE"""
    assert_that(event_tracer).described_as(
        f"All three: TMC Subarray Node device "
        f"({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to IDLE."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    )


@then("the DishMaster transitions to pointingState READY")
def verify_pointing_state_after_end(
    event_tracer: TangoEventTracer,
    dishes: DishesFacade,
):
    """Verify that each DishMaster transitions to
    pointingState READY"""
    for dish_id in DISH_IDS:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to READY pointingState"
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )
