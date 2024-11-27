"""Configurations needed for the tests using the new harness."""

from dataclasses import dataclass
from typing import Any

import pytest
from assertpy import assert_that
from pytest_bdd import given, then
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.init.test_harness_builder import (
    TestHarnessBuilder,
)
from ska_integration_test_harness.inputs.dish_mode import DishMode
from ska_integration_test_harness.inputs.json_input import DictJSONInput
from ska_integration_test_harness.inputs.pointing_state import PointingState
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_integration_test_harness.structure.telescope_wrapper import (
    TelescopeWrapper,
)
from ska_tango_testing.integration import TangoEventTracer, log_events
from tests.system_level_tests.utils.json_file_input_handler import (
    MyFileJSONInput,
)

TIMEOUT = 100
# ------------------------------------------------------------
# Test Harness fixtures

DEFAULT_VCC_CONFIG_INPUT = DictJSONInput(
    {
        "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
        "tm_data_sources": [
            "car://gitlab.com/ska-telescope/ska-telmodel-data?"
            + "ska-sdp-tmlite-repository-1.0.0#tmdata"
        ],
        "tm_data_filepath": (
            "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json",
        ),
    }
)
ASSERTIONS_TIMEOUT = 60

DISH_IDS = ["dish_001", "dish_036", "dish_063", "dish_100"]


@pytest.fixture
def telescope_wrapper(
    default_commands_inputs: TestHarnessInputs,
) -> TelescopeWrapper:
    """Create an unique test harness with proxies to all devices."""
    test_harness_builder = TestHarnessBuilder()

    # import from a configuration file device names and emulation directives
    # for TMC, CSP, SDP and the Dishes
    test_harness_builder.read_config_file(
        "mid/tests/system_level_tests/test_harness_config.yaml"
    )
    test_harness_builder.validate_configurations()

    # set the default inputs for the TMC commands,
    # which will be used for teardown procedures
    test_harness_builder.set_default_inputs(default_commands_inputs)
    test_harness_builder.validate_default_inputs()

    # build the wrapper of the telescope and its sub-systems
    telescope = test_harness_builder.build()
    telescope.actions_default_timeout = 300
    yield telescope
    # after a test is completed, reset the telescope to its initial state
    # (obsState=READY, telescopeState=OFF, no resources assigned)
    telescope.tear_down()


@pytest.fixture
def default_commands_inputs() -> TestHarnessInputs:
    """Default JSON inputs for TMC commands."""
    return TestHarnessInputs(
        assign_input=MyFileJSONInput("centralnode", "assign_resources_mid"),
        configure_input=MyFileJSONInput("subarray", "configure_mid"),
        scan_input=MyFileJSONInput("subarray", "scan_mid"),
        release_input=MyFileJSONInput("centralnode", "release_resources_mid"),
        default_vcc_config_input=DEFAULT_VCC_CONFIG_INPUT,
    )


@pytest.fixture
def tmc(telescope_wrapper: TelescopeWrapper) -> TMCFacade:
    """Create a facade to TMC devices."""
    return TMCFacade(telescope_wrapper)


@pytest.fixture
def csp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to CSP devices."""
    return CSPFacade(telescope_wrapper)


@pytest.fixture
def sdp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to SDP devices."""
    return SDPFacade(telescope_wrapper)


@pytest.fixture
def dishes(telescope_wrapper: TelescopeWrapper):
    """Create a facade to dishes devices."""
    return DishesFacade(telescope_wrapper)


# Tango event tracer


@pytest.fixture
def event_tracer() -> TangoEventTracer:
    """Create an event tracer."""
    return TangoEventTracer(
        event_enum_mapping={
            "obsState": ObsState,
            "dishMode": DishMode,
            "poitingState": PointingState,
        },
    )


@given("a Mid telescope")
def given_the_sut(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    dishes: DishesFacade,
):
    """
    Telescope consisting of csp , sdp and dish devices
    """
    event_tracer.subscribe_event(tmc.central_node, "telescopeState")
    event_tracer.subscribe_event(csp.csp_master, "State")
    event_tracer.subscribe_event(csp.csp_subarray, "State")
    event_tracer.subscribe_event(sdp.sdp_master, "State")
    event_tracer.subscribe_event(sdp.sdp_subarray, "State")

    for dish_id in DISH_IDS:
        event_tracer.subscribe_event(
            dishes.dish_master_dict[dish_id], "dishMode"
        )
        event_tracer.subscribe_event(
            dishes.dish_master_dict[dish_id], "pointingState"
        )

    log_events(
        {
            tmc.central_node: ["telescopeState"],
            csp.csp_master: ["State"],
            csp.csp_subarray: ["State"],
        }
    )
    log_events(
        {
            sdp.sdp_master: ["State"],
            sdp.sdp_subarray: ["State"],
        }
    )
    for dish_id in DISH_IDS:
        log_events(
            {
                dishes.dish_master_dict[dish_id]: ["dishMode"],
            },
            event_enum_mapping={"DishMode": DishMode},
        )


@given("a Telescope consisting of SDP, CSP and DISH that is OFF")
def check_state_is_off(
    tmc: TMCFacade,
):
    """Send the ON command to the telescope."""
    tmc.move_to_off(wait_termination=True)


@given("a Telescope consisting of SDP, CSP and DISH that is ON")
def check_state_is_on(
    tmc: TMCFacade,
):
    """Send the ON command to the telescope."""
    tmc.move_to_on(wait_termination=True)


@then("DishMaster must transition to STANDBY-LP mode")
def verify_dish_mode_standby_lp(
    event_tracer: TangoEventTracer,
    dishes: DishesFacade,
):
    """Verify that each DishMaster transitions to the STANDBY-LP"""

    # Iterate over dish IDs and verify the transition of each DishMaster
    for dish_id in DISH_IDS:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to STANDBY-LP mode"
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )


@dataclass
class SubarrayTestContextData:
    """A class to store shared variables between steps."""

    starting_state: ObsState | None = None
    """The state of the system before the WHEN step."""

    expected_next_state: ObsState | None = None
    """The expected state to be reached if no WHEN step is executed.

    It is meaningful when the starting state is transient and so it will
    automatically change to another state (different both from the starting
    state and the expected next state).

    Leave empty if the starting state is not transient.
    """

    when_action_result: Any | None = None
    """The result of the WHEN step command."""

    when_action_name: str | None = None
    """The name of the Tango command executed in the WHEN step."""

    def is_starting_state_transient(self) -> bool:
        """Check if the starting state is transient."""
        return self.expected_next_state is not None


@pytest.fixture
def context_fixt() -> SubarrayTestContextData:
    """A collection of variables shared between steps.

    The shared variables are the following:

    - previous_state: the previous state of the subarray.
    - expected_next_state: the expected next state of the subarray (specified
        only if the previous st
    - trigger: the trigger that caused the state change.

    :return: the shared variables.
    """
    return SubarrayTestContextData()


def _setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up event subscriptions for the test.

    Args:
        subarray_node_facade: Facade for the TMC subarray node.
        csp: Facade for the CSP.
        event_tracer: Event tracer for capturing events.
    """
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(tmc.subarray_node, "assignedResources")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
                "assignedResources",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState"],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


def _get_long_run_command_id(context_fixt: SubarrayTestContextData) -> str:
    return context_fixt.when_action_result[1][0]


def get_expected_long_run_command_result(context_fixt) -> tuple[str, str]:
    return (
        _get_long_run_command_id(context_fixt),
        f'[{ResultCode.OK.value}, "Command Completed"]',
    )


@given("subarray is in the IDLE obsState")
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt.starting_state = ObsState.IDLE

    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )


@then("the TMC, CSP and SDP subarrays transition to RESOURCING obsState")
def verify_resourcing_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the RESOURCING state.
    """
    assert_that(event_tracer).described_as(
        f"All three: TMC Subarray Node device "
        f"({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to RESOURCING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt.starting_state,
    )

    # override the starting state for the next step
    context_fixt.starting_state = ObsState.RESOURCING


@then(
    "the TMC receives LongRunningCommandResult event OK "
    "from subsystems CSP and SDP"
)
def assert_long_running_command_completion(
    event_tracer,
    tmc: TMCFacade,
    context_fixt,
):
    """
    Asserts that the TMC Central Node reports a successful
    completion of a long-running command.
    """
    assert_that(event_tracer).described_as(
        f"TMC Central Node ({tmc.central_node}) is "
        " expected to report a longRunningCommand successful completion."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        get_expected_long_run_command_result(context_fixt),
    )


@then(
    "the TMC receives LongRunningCommandResult event OK from subsystems "
    "CSP, SDP and DISH"
)
def verify_long_running_command_result_on_subarray(
    event_tracer,
    tmc: TMCFacade,
    context_fixt,
):
    """
    Asserts that the TMC Subarray Node reports a successful
    completion of a long-running command.
    """
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node ({tmc.subarray_node}) is "
        " expected to report a longRunningCommand successful completion."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        get_expected_long_run_command_result(context_fixt),
    )


@given("subarray is in the READY obsState")
def subarray_in_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    tmc.force_change_of_obs_state(
        ObsState.READY,
        default_commands_inputs,
        wait_termination=True,
    )
    context_fixt.starting_state = ObsState.READY

    # We haven't used force change obstate directly as we are not able to
    # verify the completion of command with longrunningcommandresult against
    # the command_id

    # context_fixt.when_action_name = "AssignResources"
    # json_input = MyFileJSONInput(
    #     "centralnode", "assign_resources_mid"
    # ).with_attribute("subarray_id", 1)

    # context_fixt.when_action_result = tmc.assign_resources(
    #     json_input,
    #     wait_termination=False,
    # )
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to RESOURCING."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.RESOURCING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.RESOURCING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.RESOURCING,
    #     previous_value=context_fixt.starting_state,
    # )

    # # override the starting state for the next step

    # context_fixt.starting_state = ObsState.RESOURCING
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to IDLE."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.IDLE,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.IDLE,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.IDLE,
    #     previous_value=context_fixt.starting_state,
    # )
    # assert_that(event_tracer).described_as(
    #     f"TMC Central Node ({tmc.central_node}) is "
    #     " expected to report a longRunningCommand successful completion."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.central_node,
    #     "longRunningCommandResult",
    #     get_expected_long_run_command_result(context_fixt),
    # )
    # context_fixt.starting_state = ObsState.IDLE
    # context_fixt.when_action_name = "Configure"
    # json_input = MyFileJSONInput("subarray", "configure_mid")
    # context_fixt.when_action_result = tmc.configure(
    #     json_input,
    #     wait_termination=False,
    # )
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to CONFIGURING."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.CONFIGURING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.CONFIGURING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.CONFIGURING,
    #     previous_value=context_fixt.starting_state,
    # )
    # # store current (already verified) state to use it as previous step
    # # in next assertions
    # context_fixt.starting_state = ObsState.CONFIGURING
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to READY."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=context_fixt.starting_state,
    # )
    # assert_that(event_tracer).described_as(
    #     f"TMC Subarray Node ({tmc.subarray_node}) is "
    #     " expected to report a longRunningCommand successful completion."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "longRunningCommandResult",
    #     get_expected_long_run_command_result(context_fixt),
    # )
