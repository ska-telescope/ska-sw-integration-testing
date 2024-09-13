import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, List

from astropy.time import Time
from numpy import array_equal
from ska_ser_logging import configure_logging
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from ska_tango_testing.mock.placeholders import Anything
from tango import Database, DeviceProxy

from Mid.tests.resources.test_harness.constant import device_dict
from Mid.tests.resources.test_harness.event_recorder import EventRecorder
from Mid.tests.resources.test_harness.simulator_factory import SimulatorFactory
from Mid.tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    get_subarray_input_json,
)
from Mid.tests.resources.test_harness.utils.enums import SimulatorDeviceType
from Mid.tests.resources.test_harness.utils.wait_helpers import Waiter, watch
from Mid.tests.resources.test_support.common_utils.common_helpers import Resource
from Mid.tests.resources.test_support.constant import (
    csp_subarray1,
    sdp_subarray1,
    tmc_csp_subarray_leaf_node,
    tmc_sdp_subarray_leaf_node,
    tmc_subarraynode1,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
TIMEOUT = 20
EB_PB_ID_LENGTH = 15

SDP_SIMULATION_ENABLED = os.getenv("SDP_SIMULATION_ENABLED")
CSP_SIMULATION_ENABLED = os.getenv("CSP_SIMULATION_ENABLED")
DISH_SIMULATION_ENABLED = os.getenv("DISH_SIMULATION_ENABLED")

INITIAL_MID_DELAY_JSON = {
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


def check_subarray_obs_state(obs_state=None, timeout=100, subarray_node=None):
    device_dict = {
        "sdp_subarray": sdp_subarray1,
        "csp_subarray": csp_subarray1,
        "tmc_subarraynode": tmc_subarraynode1,
        "csp_subarray_leaf_node": tmc_csp_subarray_leaf_node,
        "sdp_subarray_leaf_node": tmc_sdp_subarray_leaf_node,
    }

    LOGGER.info(
        f"{tmc_subarraynode1}.obsState : "
        + str(Resource(tmc_subarraynode1).get("obsState"))
    )
    LOGGER.info(
        f"{sdp_subarray1}.obsState : "
        + str(Resource(sdp_subarray1).get("obsState"))
    )
    LOGGER.info(
        f"{csp_subarray1}.obsState : "
        + str(Resource(csp_subarray1).get("obsState"))
    )
    if obs_state == "READY" and subarray_node:
        device_dict["dish_master_list"] = subarray_node.dish_master_list
        device_dict["dish_leaf_node_list"] = subarray_node.dish_leaf_node_list

    the_waiter = Waiter(**device_dict)
    the_waiter.set_wait_for_obs_state(obs_state=obs_state)
    the_waiter.wait(timeout / 0.1)

    return all(
        [
            Resource(sdp_subarray1).get("obsState") == obs_state,
            Resource(tmc_subarraynode1).get("obsState") == obs_state,
            Resource(csp_subarray1).get("obsState") == obs_state,
        ]
    )


def get_device_simulators(simulator_factory):
    """A method to get simulators for Subsystem devices

    Args:
        simulator_factory (fixture): fixture for SimulatorFactory class,
        which provides simulated subarray and master devices

    Returns:
        simulator(sim) objects
    """
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_DEVICE
    )
    dish_sim_1 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=1
    )
    dish_sim_2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=2
    )
    dish_sim_3 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=3
    )
    dish_sim_4 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=4
    )
    return csp_sim, sdp_sim, dish_sim_1, dish_sim_2, dish_sim_3, dish_sim_4


def get_master_device_simulators(simulator_factory):
    """A method to get simulators for Subsystem master devices

    Args:
        simulator_factory (fixture): fixture for SimulatorFactory class,
        which provides simulated subarray and master devices

    Returns:
        simulator(sim) objects
    """
    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_MASTER_DEVICE
    )
    dish_master_sim_1 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=1
    )
    dish_master_sim_2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=2
    )
    dish_master_sim_3 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=3
    )
    dish_master_sim_4 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE, sim_number=4
    )
    return (
        csp_master_sim,
        sdp_master_sim,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    )


def get_non_sidereal_json_for_now() -> tuple[str, str]:
    """Return the json for Configure command with visible non-sidereal object
    according to current time.
    """
    current_time = int(datetime.utcnow().strftime("%H"))
    configure_input_json = json.loads(
        get_subarray_input_json("configure_non_sidereal")
    )
    # The data below is losely based on information found from the web, and has
    # loose limits such that elevation is >= 17.5 for the source at
    # "lat": -30.71329, "lon": 21.449412 and "h": 1098.074 for dish SKA001
    # based on TelModel-data
    if 8 <= current_time <= 14:
        configure_input_json["pointing"]["target"]["target_name"] = "Sun"
        return (json.dumps(configure_input_json), "Sun")
    if 3 <= current_time <= 8:
        configure_input_json["pointing"]["target"]["target_name"] = "Mars"
        return (json.dumps(configure_input_json), "Mars")
    if current_time <= 3 or current_time >= 21:
        configure_input_json["pointing"]["target"]["target_name"] = "Saturn"
        return (json.dumps(configure_input_json), "Saturn")
    if 17 <= current_time <= 21:
        configure_input_json["pointing"]["target"]["target_name"] = "Pluto"
        return (json.dumps(configure_input_json), "Pluto")
    if 14 <= current_time <= 15:
        configure_input_json["pointing"]["target"]["target_name"] = "Venus"
        return (json.dumps(configure_input_json), "Venus")
    return ("", "")


def get_device_simulator_with_given_name(simulator_factory, devices):
    """Get Device type based on device name and return device proxy
    Args:
        devices (list): simulator devices list
    """
    device_name_type_dict = {
        "csp subarray": SimulatorDeviceType.MID_CSP_DEVICE,
        "sdp subarray": SimulatorDeviceType.MID_SDP_DEVICE,
        "csp master": SimulatorDeviceType.MID_CSP_MASTER_DEVICE,
        "sdp master": SimulatorDeviceType.MID_SDP_MASTER_DEVICE,
        "dish master1": SimulatorDeviceType.DISH_DEVICE,
    }
    sim_device_proxy_list = []
    for device_name in devices:
        if device_name in device_name_type_dict:
            sim_device_type = device_name_type_dict[device_name]
            sim_device_proxy_list.append(
                simulator_factory.get_or_create_simulator_device(
                    sim_device_type
                )
            )
        elif device_name.startswith("dish"):
            sim_number = device_name.split()[-1]
            sim_device_proxy_list.append(
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.DISH_DEVICE, sim_number=int(sim_number)
                )
            )
    return sim_device_proxy_list


def prepare_json_args_for_commands(
    args_for_command: str, command_input_factory: JsonFactory
) -> str:
    """This method return input json based on command args"""
    if args_for_command is not None:
        input_json = command_input_factory.create_subarray_configuration(
            args_for_command
        )
    else:
        input_json = None
    return input_json


def prepare_json_args_for_centralnode_commands(
    args_for_command: str, command_input_factory: JsonFactory
) -> str:
    """This method return input json based on command args"""
    if args_for_command is not None:
        input_json = command_input_factory.create_centralnode_configuration(
            args_for_command
        )
    else:
        input_json = None
    return input_json


def prepare_schema_for_attribute_or_command(
    args_for_command: str, command_input_factory: JsonFactory
):
    """This method return schema for requested command or attribute json."""
    if args_for_command is not None:
        input_json = command_input_factory.create_command_or_attribute_schema(
            args_for_command
        )
    else:
        input_json = None
    return input_json


def get_boolean_command_call_info(device: SimulatorFactory, command_name: str):
    """
    Returns recorded information from commandCallInfo attribute.
    This function is used when expected information is of type boolean.
    device: Tango Device Proxy Object

    """
    command_call_info = device.read_attribute("commandCallInfo").value
    LOGGER.info("Command info %s", command_call_info)
    command_info = [
        command_info
        for command_info in command_call_info
        if command_info[0] == command_name
    ]

    received_command_call_data = (
        command_call_info[0][0],
        command_info[0][1],
    )

    return received_command_call_data


def get_command_call_info(device: Any, command_name: str):
    """
    Returns recorded information from commandCallInfo attribute.
    This function is used when expected information is json
    device: Tango Device Proxy Object

    """
    command_call_info = device.read_attribute("commandCallInfo").value
    LOGGER.info("Command info %s", command_call_info)
    command_info = [
        command_info
        for command_info in command_call_info
        if command_info[0] == command_name
    ]

    input_str = json.loads("".join(command_info[0][1].split()))

    received_command_call_data = (
        command_call_info[0][0],
        sorted(input_str),
    )

    return received_command_call_data


def device_received_this_command(
    device: Any, expected_command_name: str, expected_input: str | bool
) -> bool:
    """Method to verify received command and command argument

    Args:
        device (Any): Tango Device Proxy Object
        expected_command_name (str): Command name received on simulator device
        expected_input (str): Command argument received on simulator device

    Returns:
        Boolean: True if received data is equal to expected data.
    """

    LOGGER.debug("expected_input - %s", expected_input)

    if (
        expected_input == "True"
        or expected_input == "False"
        or expected_input == ""
    ):
        received_command_call_data = get_boolean_command_call_info(
            device, expected_command_name
        )
        LOGGER.debug(
            "received_command_call_data - %s", received_command_call_data
        )

        LOGGER.debug("expected_input %s", expected_input)
        return received_command_call_data == (
            expected_command_name,
            expected_input,
        )

    else:
        received_command_call_data = get_command_call_info(
            device, expected_command_name
        )
        LOGGER.debug(
            "received_command_call_data - %s", received_command_call_data
        )

        expected_input_str = json.loads("".join(expected_input.split()))
        LOGGER.debug("expected_input_str %s", expected_input_str)
        return received_command_call_data == (
            expected_command_name,
            sorted(expected_input_str),
        )


def get_recorded_commands(device: Any):
    """A method to get data from simulator device

    Args:
        device (Any): Tango Device Proxy Object

    Returns: List[tuple]
        recorded data from Simulator device
    """
    return device.read_attribute("commandCallInfo").value


def set_desired_health_state(
    sim_devices_list: list, health_state_value: HealthState
):
    """A method to set simulator devices healthState attribute

    Args:
        sim_devices_list: simulator devices list
        health_state_value: desired healthState value to set
    """

    for device in sim_devices_list:
        device.SetDirectHealthState(health_state_value)
        device.SetDirectHealthState(health_state_value)
        device.SetDirectHealthState(health_state_value)
        device.SetDirectHealthState(health_state_value)


def check_assigned_resources(device: Any, receiptor_ids: tuple):
    """
    Method to verify assignedResources attribute value on subarraynode
    Args:
        device : tango device proxy object.
        receiptor_ids: dish ids.
    """
    assigned_resources = device.read_attribute("assignedResources").value
    LOGGER.info(f"assigned Resources:{assigned_resources}")
    return assigned_resources == receiptor_ids


def device_attribute_changed(
    device: Any,
    attribute_name_list: list,
    attribute_value_list: list,
    timeout: int,
):
    """
    Method to verify device attribute changed to speicified attribute value
    """

    def is_value_same(old_value, new_value):
        # Validate old and new value same
        return json.loads(old_value) == json.loads(new_value)

    waiter = Waiter()
    for attribute_name, attribute_value in zip(
        attribute_name_list, attribute_value_list
    ):
        waiter.waits.append(
            watch(Resource(device.dev_name())).to_become(
                attribute_name, attribute_value, predicate=is_value_same
            )
        )
    try:
        waiter.wait(timeout)
    except Exception:
        return False
    return True


def wait_for_attribute_update(
    device, attribute_name: str, expected_id: str, expected_result: ResultCode
):
    """Wait for the attribute to reflect necessary changes."""
    start_time = time.time()
    elapsed_time = time.time() - start_time
    while elapsed_time <= TIMEOUT:
        unique_id, result = device.read_attribute(attribute_name).value
        if expected_id in unique_id:
            LOGGER.info("The attribute value is: %s, %s", unique_id, result)
            return result == str(expected_result.value)
        time.sleep(1)
        elapsed_time = time.time() - start_time
    return False


def wait_till_delay_values_are_populated(
    csp_subarray_leaf_node,
) -> None:
    start_time = time.time()
    time_elapsed = 0
    while csp_subarray_leaf_node.delayModel == "" or time_elapsed <= TIMEOUT:
        time.sleep(1)
        time_elapsed = time.time() - start_time
    delay_generated_time = datetime.now()
    delay_json = csp_subarray_leaf_node.delayModel
    delay_json_dict = json.loads(delay_json)
    if csp_subarray_leaf_node.delayModel == "" and time_elapsed > TIMEOUT:
        raise Exception(
            "Timeout while waiting for CspSubarrayLeafNode to generate \
                delay values."
        )
    return delay_json_dict, delay_generated_time


def wait_for_delay_updates_stop_on_delay_model(csp_subarray_leaf_node) -> None:
    start_time = time.time()
    time_elapsed = 0
    while (
        json.loads(csp_subarray_leaf_node.delayModel) != INITIAL_MID_DELAY_JSON
        and time_elapsed <= TIMEOUT
    ):
        time.sleep(1)
        time_elapsed = time.time() - start_time
    LOGGER.info(f"time_elapsed: {time_elapsed}")
    if time_elapsed > TIMEOUT:
        raise Exception(
            "Timeout while waiting for CspSubarrayLeafNode to generate \
                delay values."
        )


def is_last_pointing_data_updated(dish_leaf_node, timeout=50) -> bool:
    start_time = time.time()
    time_elapsed = 0
    while (
        dish_leaf_node.lastPointingData == "Not Set"
        and time_elapsed <= timeout
    ):
        time.sleep(1)
        time_elapsed = time.time() - start_time
    LOGGER.info(
        "time_elapsed: %s and last pointing data is %s",
        time_elapsed,
        dish_leaf_node.lastPointingData,
    )
    if time_elapsed > timeout:
        raise Exception(
            "Timeout while waiting for Dish Leaf Node to generate \
                last pointing data."
        )
    return True


def generate_ska_epoch_tai_value() -> Time:
    """
    Generating SKA Epoch in TAI format

    :return: ska_epoch_tai
    :rtype: Time
    """
    SKA_EPOCH = "1999-12-31T23:59:28Z"
    ska_epoch_utc = Time(SKA_EPOCH, scale="utc")
    ska_epoch_tai = ska_epoch_utc.unix_tai
    return ska_epoch_tai


def calculate_epoch_difference(
    delay_generated_time: Time, ska_epoch_tai: Time, delay_json_dict: dict
) -> int:
    """
    Calculate Difference between epoch in delay model json and
    epoch calculated through delay generated timestamp

    :return: epoch_difference
    :rtype: int
    """
    delay_generated_time_utc = Time(delay_generated_time, scale="utc")
    delay_generated_time_tai = delay_generated_time_utc.unix_tai
    epoch = delay_generated_time_tai - ska_epoch_tai
    epoch_in_json = delay_json_dict["start_validity_sec"]
    epoch_difference = epoch_in_json - epoch
    return epoch_difference


def get_simulated_devices_info() -> dict:
    """
    A method to get simulated devices present in the deployment.

    return: dict
    """

    is_csp_simulated = CSP_SIMULATION_ENABLED.lower() == "true"
    is_sdp_simulated = SDP_SIMULATION_ENABLED.lower() == "true"
    is_dish_simulated = DISH_SIMULATION_ENABLED.lower() == "true"
    return {
        "csp_and_sdp": all(
            [is_csp_simulated, is_sdp_simulated, not is_dish_simulated]
        ),  # real DISH.LMC enabled
        "csp_and_dish": all(
            [is_csp_simulated, is_dish_simulated, not is_sdp_simulated]
        ),  # real SDP enabled
        "sdp_and_dish": all(
            [is_sdp_simulated, is_dish_simulated, not is_csp_simulated]
        ),  # real CSP.LMC enabled
        "sdp": all(
            [is_sdp_simulated, not is_csp_simulated, not is_dish_simulated]
        ),
        "all_mocks": all(
            [
                is_csp_simulated,
                is_sdp_simulated,
                is_dish_simulated,
            ]
        ),
    }


SIMULATED_DEVICES_DICT = get_simulated_devices_info()


def wait_csp_master_off():
    wait = Waiter(**device_dict)
    wait.set_wait_for_csp_master_to_become_off()
    wait.wait(500)


def generate_id(id_pattern: str) -> str:
    """
    Generate a time-based unique id.

    :param id_pattern: the string pattern as to how the unique id should
        be rendered.
        e.g :
            input: eb-mvp01-********-*****
            output: eb-mvp01-35825416-12979

    :return: the id rendered according to the requested pattern
    """
    prefix, suffix = re.split(r"(?=\*)[\*-]*(?<=\*)", id_pattern)
    id_pattern = re.findall(r"(?=\*)[\*-]*(?<=\*)", id_pattern)[0]
    length = id_pattern.count("*")
    assert length <= EB_PB_ID_LENGTH
    LOGGER.info(f"<SB or PB ID >Length: {length}")
    timestamp = str(datetime.now().timestamp()).replace(".", "")
    sections = id_pattern.split("-")
    unique_id = ""
    sections.reverse()
    for section in sections:
        section_length = len(section)
        section_id = timestamp[-section_length:]
        timestamp = timestamp[:-section_length]
        if unique_id:
            unique_id = f"{section_id}-{unique_id}"
        else:
            unique_id = section_id
    return f"{prefix}{unique_id}{suffix}"


def generate_eb_pb_ids(input_json: dict):
    """
    Method to generate different eb_id and pb_id

    :param input_json: json to utilised to update values.
    """
    input_json["sdp"]["execution_block"]["eb_id"] = generate_id(
        "eb-mvp01-********-*****"
    )
    for pb in input_json["sdp"]["processing_blocks"]:
        pb["pb_id"] = generate_id("pb-mvp01-********-*****")


def check_subarray_instance(device, subarray_id):
    """
    Method to check subarray instance
    """
    subarray = str(device).split("/")
    subarray_instance = subarray[-1][-2]
    assert subarray_instance == subarray_id


def wait_and_validate_device_attribute_value(
    device: DeviceProxy,
    attribute_name: str,
    expected_value: str,
    is_json: bool = False,
    is_list: bool = False,
    timeout: int = 300,
):
    """This method wait and validate if attribute value is equal to provided
    expected value
    """
    count = 0
    error = ""
    while count <= timeout:
        try:
            attribute_value = device.read_attribute(attribute_name).value
            logging.info(
                "%s current %s value: %s",
                device.name(),
                attribute_name,
                attribute_value,
            )
            if is_json and json.loads(attribute_value) == json.loads(
                expected_value
            ):
                return True
            elif is_list:
                return array_equal(attribute_value, json.loads(expected_value))
            elif attribute_value == expected_value:
                return True
        except Exception as e:
            # Device gets unavailable due to restart and the above command
            # tries to access the attribute resulting into exception
            # It keeps it printing till the attribute is accessible
            # the exception log is suppressed by storing into variable
            # the error is printed later into the log in case of failure
            error = e
        count += 10
        # When device restart it will at least take 10 sec to up again
        # so added 10 sec sleep and to avoid frequent attribute read.
        time.sleep(10)

    logging.exception(
        "Exception occurred while reading attribute %s and cnt is %s",
        error,
        count,
    )
    return False


def update_eb_pb_ids(input_json: str) -> str:
    """
    Method to generate different eb_id and pb_id
    :param input_json: json to utilised to update values.
    """
    input_json = json.loads(input_json)
    input_json["sdp"]["execution_block"]["eb_id"] = generate_id("eb-test")
    for pb in input_json["sdp"]["processing_blocks"]:
        pb["pb_id"] = generate_id("pb-test")
    input_json = json.dumps(input_json)
    return input_json


def update_scan_type(configure_json: str, json_value: str) -> str:
    """
    Method to update json with different scan type
    :param configure_json: json to utilised to update values.

    :param json_value: new json value to be updated in json
    """
    input_json = json.loads(configure_json)
    input_json["sdp"]["scan_type"] = json_value
    input_json = json.dumps(input_json)
    return input_json


def update_scan_id(input_json: str, scan_id: int) -> str:
    """
    Method to update scan_id in input json..
    :param input_json: json to utilised to update values.

    :param json_value: new json value to be updated in json
    """
    input_json = json.loads(input_json)
    input_json["scan_id"] = int(scan_id)
    updated_json = json.dumps(input_json)
    return updated_json


def check_long_running_command_status(
    device, lrcr_command, command_name, status
):
    """This function will validate the longRunningCommandStatus"""
    event_recorder = EventRecorder()
    event_recorder.subscribe_event(
        device,
        lrcr_command,
    )
    start_time = time.time()
    elapsed_time = 0
    timeout = 2
    while elapsed_time < timeout:
        assertion_data = event_recorder.has_change_event_occurred(
            device,
            lrcr_command,
            (Anything),
            lookahead=7,
        )
        LOGGER.info("Assertion Data: %s", assertion_data)
        iterator = iter(assertion_data["attribute_value"])
        for value in iterator:
            if value.endswith(command_name):
                if next(iterator) == status:
                    return True
        time.sleep(0.1)
        elapsed_time = time.time() - start_time
    return False


def check_for_device_command_event(
    device: DeviceProxy,
    attr_name: str,
    event_data: str,
    event_recorder: EventRecorder,
    command_name: str,
) -> bool:
    """Method to check event from the device.

    Args:
        device (DeviceProxy): device proxy
        attr_name (str): attribute name
        event_data (str): event data to be searched
        event_recorder(EventRecorder): event recorder instance
        to check for events.
        command_name(str): executed command name
    """
    event_found: bool = False
    timeout: int = 100
    elapsed_time: float = 0
    start_time: float = time.time()
    while not event_found and elapsed_time < timeout:
        assertion_data = event_recorder.has_change_event_occurred(
            device,
            attribute_name=attr_name,
            attribute_value=(Anything, Anything),
        )
        LOGGER.info("The assertion data is %s", assertion_data)
        if assertion_data["attribute_value"][0].endswith(command_name):
            if event_data in assertion_data["attribute_value"][1]:
                event_found = True
                return event_found

        elapsed_time = time.time() - start_time

    return event_found


def retry_tango_command(
    device: DeviceProxy, command_name: str, argin=None
) -> bool:
    """Method which will invoke command if Dev Error is received"""

    retry = 0
    while retry <= 3:
        try:
            device.command_inout(command_name, argin)

            break
        except Exception as e:
            LOGGER.exception(
                "Exception occurred while executing command: %s", e
            )
            if retry == 2:
                return False
            retry += 1
        time.sleep(0.1)
    return True


def check_devices_operational(devices_to_monitor: List[str]) -> bool:
    """Checks if all devices are exported in Tango DB"""
    database = Database()
    device_names = database.get_device_exported("*")
    LOGGER.debug("device_names: %s", device_names)

    operational_flags = []
    for device in devices_to_monitor:

        instance_info = database.get_device_info(device)

        LOGGER.info("instance_info: %s", instance_info)
        if instance_info.exported:
            operational_flags.append(True)
        else:
            operational_flags.append(False)

    return all(operational_flags)


def wait_until_devices_operational(devices_to_monitor):
    """Waits until devices are operational or timeout is reached."""
    start_time = time.time()
    TIMEOUT = 30

    while time.time() - start_time < TIMEOUT:
        try:
            if check_devices_operational(devices_to_monitor):
                return True  # Devices are operational, exit function
        except Exception as exception:
            LOGGER.info(
                "Error while checking devices operational: %s", exception
            )

        time.sleep(1)

    LOGGER.info(
        "Timeout of %d seconds reached. Devices are not operational.", TIMEOUT
    )
    return False
