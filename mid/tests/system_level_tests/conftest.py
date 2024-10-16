"""Configurations needed for the tests using the new harness."""


import pytest
from assertpy import assert_that
from pytest_bdd import given, then
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
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


@pytest.fixture
def telescope_wrapper(
    default_commands_inputs: TestHarnessInputs,
) -> TelescopeWrapper:
    """Create an unique test harness with proxies to all devices."""
    test_harness_builder = TestHarnessBuilder()

    # import from a configuration file device names and emulation directives
    # for TMC, CSP, SDP and the Dishes
    test_harness_builder.read_config_file(
        # "tests/system_level_tests/test_harness_config.yaml"
        "mid/tests/system_level_tests/test_harness_config.yaml"
    )
    test_harness_builder.validate_configurations()

    # set the default inputs for the TMC commands,
    # which will be used for teardown procedures
    test_harness_builder.set_default_inputs(default_commands_inputs)
    test_harness_builder.validate_default_inputs()

    # build the wrapper of the telescope and it's sub-systems
    telescope = test_harness_builder.build()
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
def central_node_facade(telescope_wrapper: TelescopeWrapper):
    """Create a facade to TMC central node and all its operations."""
    central_node_facade = TMCCentralNodeFacade(telescope_wrapper)
    yield central_node_facade


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


@given("a mid telescope")
def given_the_sut(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    dishes: DishesFacade,
):
    """
    Telescope consisting of csp , sdp and dish devices
    """
    event_tracer.subscribe_event(
        central_node_facade.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(csp.csp_master, "State")
    event_tracer.subscribe_event(csp.csp_subarray, "State")
    event_tracer.subscribe_event(sdp.sdp_master, "State")
    event_tracer.subscribe_event(sdp.sdp_subarray, "State")

    for dish_id in ["dish_001", "dish_036", "dish_063", "dish_100"]:
        event_tracer.subscribe_event(
            dishes.dish_master_dict[dish_id], "dishMode"
        )
        event_tracer.subscribe_event(
            dishes.dish_master_dict[dish_id], "pointingState"
        )

    log_events(
        {
            central_node_facade.central_node: ["telescopeState"],
            csp.csp_master: ["State"],
            csp.csp_subarray: ["State"],
        }
    )
    log_events(
        {
            central_node_facade.central_node: ["telescopeState"],
            sdp.sdp_master: ["State"],
            sdp.sdp_subarray: ["State"],
        }
    )
    for dish_id in ["dish_001", "dish_036", "dish_063", "dish_100"]:
        log_events(
            {
                central_node_facade.central_node: ["telescopeState"],
                dishes.dish_master_dict[dish_id]: ["dishMode"],
            },
            event_enum_mapping={"DishMode": DishMode},
        )


@given("a Telescope consisting of SDP, CSP and DISH that is OFF")
def invoke_telescope_off_command(
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the OFF command to the telescope."""
    central_node_facade.move_to_off(wait_termination=True)


@given("a Telescope consisting of SDP, CSP and DISH that is ON")
def invoke_telescope_on_command(
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the ON command to the telescope."""
    central_node_facade.move_to_on(wait_termination=True)


@then("DishMaster must transition to STANDBY-LP mode")
def verify_dish_mode(
    event_tracer: TangoEventTracer,
    dishes: DishesFacade,
):
    """Verify that each DishMaster transitions to the correct mode."""

    # Iterate over dish IDs and verify the transition of each DishMaster
    for dish_id in ["dish_001", "dish_036", "dish_063", "dish_100"]:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to STANDBY-LP mode"
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )
