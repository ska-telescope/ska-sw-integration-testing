from dataclasses import dataclass
from typing import Any

import pytest
from ska_control_model import ObsState
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from tests.system_level_tests.utils.my_file_json_input import MyFileJSONInput


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


def subarray_in_resourcing_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the RESOURCING state."""
    context_fixt.starting_state = ObsState.RESOURCING
    context_fixt.expected_next_state = ObsState.IDLE

    subarray_node_facade.force_change_of_obs_state(
        ObsState.RESOURCING,
        default_commands_inputs,
        wait_termination=True,
    )


def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    central_node_facade: TMCCentralNodeFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt.starting_state = ObsState.IDLE

    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        default_commands_inputs,
        wait_termination=True,
    )

    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
        json_input,
        wait_termination=True,
    )
