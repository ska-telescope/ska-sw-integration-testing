import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.dish_mode import DishMode
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState
from tests.system_level_tests.conftest import DISH_IDS

# Constants
ASSERTIONS_TIMEOUT = 60


@pytest.mark.system_level_test_mid
@scenario(
    "system_level_tests/" + "xtp_66801_telescope_operational_commands.feature",
    "Starting up mid telescope",
)
def test_telescope_on_command_flow():
    """
    Test case to verify ON command on mid telescope
    """


@when("I invoke the ON command on the telescope")
def send_telescope_on_command(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
):
    """Send the ON command to the telescope."""
    event_tracer.clear_events()
    tmc.move_to_on(wait_termination=False)


@then(
    "the Telescope consisting of SDP and CSP devices "
    "must transition to ON state"
)
def verify_on_state(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """The telescope and CSP devices transition to the ON state."""
    assert_that(event_tracer).described_as(
        "The telescope,CSP and SDP devices should transition \
            from OFF to ON state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "telescopeState",
        DevState.ON,
    ).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        sdp.sdp_master,
        "State",
        DevState.ON,
    )


@then("DishMaster must transition to STANDBY-FP mode")
def verify_dish_mode_standby_fp(
    event_tracer: TangoEventTracer,
    dishes: DishesFacade,
):
    """Verify that each DishMaster transitions to the STANDBY-FP"""

    # Iterate over dish IDs and verify the transition of each DishMaster
    for dish_id in DISH_IDS:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to STANDBY-FP mode"
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
