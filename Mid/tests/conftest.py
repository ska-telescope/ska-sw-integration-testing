"""Test configuration file for ska_tmc_integration"""
import json
import logging
import os
import time
from os.path import dirname, join

import pytest
import tango
from pytest_bdd import given, parsers, then, when
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from ska_tango_testing.mock.tango.event_callback import (
    MockTangoEventCallbackGroup,
)
from tango import DevState

from Mid.tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from Mid.tests.resources.test_harness.constant import centralnode, csp_master
from Mid.tests.resources.test_harness.event_recorder import EventRecorder
from Mid.tests.resources.test_harness.helpers import (
    CSP_SIMULATION_ENABLED,
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    wait_and_validate_device_attribute_value,
)
from Mid.tests.resources.test_harness.simulator_factory import SimulatorFactory
from Mid.tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from Mid.tests.resources.test_harness.tmc_mid import TMCMid
from Mid.tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    SharedContext,
)
from Mid.tests.resources.test_harness.utils.enums import ResultCode

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
MID_DELAYMODEL_VERSION = "https://schema.skao.int/ska-mid-csp-delaymodel/3.0"


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: :py:class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a :py:class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: :py:class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


def get_input_str(path):
    """
    Returns input json string
    :rtype: String
    """
    with open(path, "r", encoding="UTF-8") as file:
        input_arg = file.read()
    return input_arg


@pytest.fixture
def event_tracer():
    """Returns a TangoEventTracer instance."""
    return TangoEventTracer()


@pytest.fixture()
def json_factory():
    """
    Json factory for getting json files
    """

    def _get_json(slug):
        return get_input_str(join(dirname(__file__), "data", f"{slug}.json"))

    return _get_json


TELESCOPE_ENV = os.getenv("TELESCOPE")

TIMEOUT = 2000


def update_configure_json(
    configure_json: str,
    scan_duration: float,
    transaction_id: str,
    scan_type: str,
    config_id: str,
) -> str:
    """
    Returns a json with updated values for the given keys
    """
    config_dict = json.loads(configure_json)

    config_dict["tmc"]["scan_duration"] = scan_duration
    config_dict["transaction_id"] = transaction_id
    config_dict["sdp"]["scan_type"] = scan_type
    config_dict["csp"]["common"]["config_id"] = config_id
    return json.dumps(config_dict)


def update_scan_json(scan_json: str, scan_id: int, transaction_id: str) -> str:
    """
    Returns a json with updated values for the given keys
    """
    scan_dict = json.loads(scan_json)

    scan_dict["scan_id"] = scan_id
    scan_dict["transaction_id"] = transaction_id
    return json.dumps(scan_dict)


@pytest.fixture()
def change_event_callbacks() -> MockTangoEventCallbackGroup:
    """subarray_node
    Return a dictionary of Tango device change event callbacks with
    asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "longRunningCommandResult",
        timeout=50.0,
    )


@pytest.fixture()
def central_node_mid() -> CentralNodeWrapperMid:
    """Return CentralNode for Mid Telescope and calls tear down"""
    central_node = CentralNodeWrapperMid()
    yield central_node
    # this will call after test complete
    central_node.tear_down()


@pytest.fixture()
def tmc_mid() -> TMCMid:
    """Return TMC Mid object"""
    tmc_mid = TMCMid()
    yield tmc_mid
    tmc_mid.tear_down()


@pytest.fixture()
def subarray_node() -> SubarrayNodeWrapper:
    """Return SubarrayNode and calls tear down"""
    subarray = SubarrayNodeWrapper()
    yield subarray
    # this will call after test complete
    subarray.tear_down()


@pytest.fixture()
def command_input_factory() -> JsonFactory:
    """Return Json Factory"""
    return JsonFactory()


@pytest.fixture()
def simulator_factory() -> SimulatorFactory:
    """Return Simulator Factory for Mid Telescope"""
    return SimulatorFactory()


@pytest.fixture()
def event_recorder() -> EventRecorder:
    """Return EventRecorder and clear events"""
    event_rec = EventRecorder()
    yield event_rec
    event_rec.clear_events()


def wait_for_dish_mode_change(
    target_mode: int, dishfqdn: str, timeout_seconds: int
):
    """Returns True if the dishMode is changed to a expected value"""
    LOGGER.info("target_mode: %s", target_mode)
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if dishfqdn.dishMode == target_mode:
            return True
        time.sleep(1)

    return False


def wait_for_telescope_state_change(
    target_state: int, centralnode_fqdn: str, timeout_seconds: int
):
    """
    Waits for the telescopeState of a central node
    to change to the specified target_state.

    Parameters:
    - target_state (int): The expected telescopeState
                          to wait for.
    - centralnode_fqdn (str): Fully Qualified Domain
                              Name (FQDN) of the central node.
    - timeout_seconds (int): Maximum time (in seconds) to
                            wait for the state change.

    Returns:
    - bool: True if the telescopeState changes
      to the target_state within the specified timeout, False otherwise.
    """

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if centralnode_fqdn.telescopeState == target_state:
            return True
        time.sleep(1)

    return False


def wait_for_pointing_state_change(
    target_mode: int, dishfqdn: str, timeout_seconds: int
):
    """Returns True if the pointingState is changed to a expected value"""
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if dishfqdn.pointingState.value == target_mode:
            return True
        time.sleep(1)

    return False


def wait_for_obsstate_state_change(
    target_mode: int, device: str, timeout_seconds: int
):
    """Returns True if the pointingState is changed to a expected value"""
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if device.obsState.value == target_mode:
            return True
        time.sleep(1)

    return False


@pytest.fixture
def shared_context():
    """
    This is used for sharing data between BDD tests
    """
    return SharedContext()


@pytest.fixture(scope="module")
def stored_unique_id():
    """
    A placeholder fixture to access
    the uniques_ids in multiple function as a parameter
    :returns: empty list
    """
    return []


@pytest.fixture(scope="session", autouse=True)
def is_dish_vcc_set():
    """
    Validate dish vcc config set to true
    """
    csp_master_device = tango.DeviceProxy(csp_master)
    if csp_master_device.adminMode != 0:
        csp_master_device.adminMode = 0
        csp_state = csp_master_device.state()
        if CSP_SIMULATION_ENABLED.lower() == "true" and csp_state in (
            tango.DevState.UNKNOWN,
            tango.DevState.DISABLE,
        ):
            csp_master_device.setdirectstate(tango.DevState.OFF)
    central_node = tango.DeviceProxy(centralnode)
    assert wait_and_validate_device_attribute_value(
        central_node,
        "isDishVccConfigSet",
        True,
    ), "Timeout while waiting for isDishVccConfigSet to true"


@given("the telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
) -> None:
    """Ensure telescope is in ON state."""
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("TMC subarray is in ObsState IDLE")
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node,
) -> None:
    """
    Move TMC Subarray to IDLE obsstate.
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    :param event_recorder: fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    :param command_input_factory: fixture for creating input required
    for command
    :param subarray_node: fixture for a TMC SubarrayNode under test
    """
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    # Create json for AssignResources commands with requested subarray_id
    assign_input = json.loads(assign_input_json)
    _, unique_id = central_node_mid.store_resources(json.dumps(assign_input))

    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps([ResultCode.OK, "Command Completed"])),
        lookahead=5,
    )


@given("CSP subarray transitioned to obsState IDLE")
def csp_subarray_is_in_idle(
    event_recorder: EventRecorder, simulator_factory: SimulatorFactory
):
    "Method to check CSP subarray is in IDLE."
    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.IDLE,
    )


@given(
    parsers.parse("TMC subarray {subarray_id} stuck in obsState RESOURCING")
)
def tmc_subarray_stuck_in_resourcing(
    subarray_node: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
    subarray_id: str,
):
    "Method to check TMC subarray stuck in Resourcing."
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@when(parsers.parse("I invoked Abort on TMC subarray {subarray_id}"))
def invoke_abort(subarray_node: SubarrayNodeWrapper, subarray_id: str):
    """
    This method invokes abort command on tmc subarray.
    """
    subarray_node.set_subarray_id(subarray_id)
    subarray_node.execute_transition("Abort")


@then("the CSP subarray transitions to ObsState ABORTED")
def sdp_csp_subarray_is_in_aborted_obsstate(
    event_recorder: EventRecorder, simulator_factory: SimulatorFactory
):
    """
    Method to check SDP subarray and CSP subarray is in ABORTED obsstate
    """
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    event_recorder.subscribe_event(csp_sim, "obsState")

    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.ABORTED,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState ABORTED"
    )
)
def tmc_subarray_is_in_aborted_obsstate(
    subarray_node: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
    subarray_id: str,
):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


MID_DELAY_JSON = {
    "interface": "https://schema.skao.int/ska-mid-csp-delaymodel/3.0",
    "start_validity_sec": 0.1,
    "cadence_sec": 0.1,
    "validity_period_sec": 0.1,
    "config_id": "",
    "subarray": 1,
    "receptor_delays": [
        {"receptor": "", "xypol_coeffs_ns": [], "ypol_offset_ns": 0.0},
        {"receptor": "", "xypol_coeffs_ns": [], "ypol_offset_ns": 0.0},
    ],
}
