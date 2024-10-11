from dataclasses import dataclass
from typing import Any

import pytest
from pytest_bdd import given, parsers
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.init.test_harness_builder import (
    TestHarnessBuilder,
)
from ska_integration_test_harness.inputs.json_input import DictJSONInput
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_integration_test_harness.structure.telescope_wrapper import (
    TelescopeWrapper,
)
from ska_tango_testing.integration import TangoEventTracer, log_events
from tests.system_level_tests.utils.my_file_json_input import MyFileJSONInput

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

    test_harness_builder.set_default_inputs(default_commands_inputs)
    test_harness_builder.validate_default_inputs()

    # build the wrapper of the telescope and its sub-systems
    telescope = test_harness_builder.build()
    yield telescope

    telescope.tear_down()


@pytest.fixture
def central_node_facade(telescope_wrapper: TelescopeWrapper):
    """Create a facade to TMC central node and all its operations."""
    central_node_facade = TMCCentralNodeFacade(telescope_wrapper)
    yield central_node_facade


@pytest.fixture
def subarray_node_facade(telescope_wrapper: TelescopeWrapper):
    """Create a facade to TMC subarray node and all its operations."""
    subarray_node = TMCSubarrayNodeFacade(telescope_wrapper)
    yield subarray_node


@pytest.fixture
def csp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to CSP devices."""
    return CSPFacade(telescope_wrapper)


@pytest.fixture
def sdp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to SDP devices."""
    return SDPFacade(telescope_wrapper)


# ----------------------------------------------------------
# Tango event tracer
@pytest.fixture
def event_tracer() -> TangoEventTracer:
    """Create an event tracer."""
    return TangoEventTracer(
        event_enum_mapping={"obsState": ObsState},
    )


# ------------------------------------------------------------
# Other fixtures and common steps
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
    central_node_facade: TMCCentralNodeFacade,
    subarray_node_facade: TMCSubarrayNodeFacade,
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
    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "obsState"
    )
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(
        central_node_facade.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "longRunningCommandResult"
    )

    log_events(
        {
            subarray_node_facade.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState"],
            central_node_facade.central_node: ["longRunningCommandResult"],
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


@given(parsers.parse("the subarray {subarray_id} can be used"))
def subarray_can_be_used(
    subarray_id: str,
    central_node_facade: TMCCentralNodeFacade,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up the subarray (and the subscriptions) to be used in the test."""
    subarray_node_facade.set_subarray_id(int(subarray_id))
    _setup_event_subscriptions(
        central_node_facade, subarray_node_facade, csp, sdp, event_tracer
    )


@given("the Telescope is in ON state")
def send_telescope_on_command(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the TelescopeOn command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.move_to_on(wait_termination=True)
