"""Configurations needed for the tests using the new harness."""


import pytest
from pytest_bdd import given
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)

# from ska_integration_test_harness.init.test_harness_builder import (
#     TestHarnessBuilder,
# )
# from ska_integration_test_harness.inputs.test_harness_inputs import (
#     TestHarnessInputs,
# )
from ska_integration_test_harness.structure.telescope_wrapper import (
    TelescopeWrapper,
)
from ska_tango_testing.integration import TangoEventTracer

# @pytest.fixture
# def telescope_wrapper(
#     default_commands_inputs: TestHarnessInputs,
# ) -> TelescopeWrapper:
#     """Create an unique test harness with proxies to all devices."""
#     test_harness_builder = TestHarnessBuilder()

#     # import from a configuration file device names and emulation directives
#     # for TMC, CSP, SDP and the Dishes
#     test_harness_builder.read_config_file(
#         "tests/tmc_csp_new_ITH/test_harness_config.yaml"
#     )
#     test_harness_builder.validate_configurations()

#     # set the default inputs for the TMC commands,
#     # which will be used for teardown procedures
#     test_harness_builder.set_default_inputs(default_commands_inputs)
#     test_harness_builder.validate_default_inputs()

#     # build the wrapper of the telescope and it's sub-systems
#     telescope = test_harness_builder.build()
#     yield telescope

#     # after a test is completed, reset the telescope to its initial state
#     # (obsState=READY, telescopeState=OFF, no resources assigned)
#     telescope.tear_down()

#     # NOTE: As the code is organized now, I cannot anticipate the
#     # teardown of the telescope structure. To run reset now I should
#     # init subarray node (with SetSubarrayId), but to do that I need
#     # to know subarray_id, which is a parameter of the Gherkin steps.


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
        event_enum_mapping={"obsState": ObsState},
    )


@given("the telescope is in ON state")
def given_the_telescope_is_in_on_state(
    central_node_facade: TMCCentralNodeFacade,
):
    """Ensure the telescope is in ON state."""
    central_node_facade.move_to_on(wait_termination=True)
