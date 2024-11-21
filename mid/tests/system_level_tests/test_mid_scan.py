"""Test module for Scan functionality (XTP-68819)"""

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
from tests.system_level_tests.conftest import SubarrayTestContextData
from tests.system_level_tests.utils.json_file_input_handler import (
    MyFileJSONInput,
)

TIMEOUT = 100


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/"
    + "xtp_66801_telescope_observational_commands.feature",
    "Execute Scan on the Mid telescope",
)
def test_telescope_scan():
    """BDD test scenario for verifying successful execution of
    the Scan command with TMC,CSP, SDP and DISH
    devices for pairwise testing"""


#  @given("telescope is in ON state") -> conftest


@when("I issue the Scan command to subarray")
def send_scan_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
):
    """
    Send the Scan command to the subarray.

    This step uses the subarray_node_facade to send a Scan command to the
    specified subarray. It uses a pre-defined JSON input file and sends
    the command without waiting for termination. The action result is
    stored in the context fixture.
    """
    context_fixt.when_action_name = "Scan"

    json_input = MyFileJSONInput("subarray", "scan_mid")

    context_fixt.when_action_result = tmc.scan(
        json_input,
        wait_termination=False,
    )


@then("the TMC, CSP and SDP subarrays transition to SCANNING obsState")
def verify_scanning_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the SCANNING state.
    """
    context_fixt.starting_state = ObsState.READY
    assert_that(event_tracer).described_as(
        "All three: TMC Subarray Node device"
        f"({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to SCANNING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.SCANNING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.SCANNING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.SCANNING,
        previous_value=context_fixt.starting_state,
    )
