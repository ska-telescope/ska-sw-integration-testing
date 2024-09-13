import json
import logging
from datetime import datetime
from typing import Any

import tango
from ska_control_model import ResultCode
from ska_ser_logging import configure_logging
from ska_tango_testing.integration.assertions import (
    _get_tracer,
    _print_passed_event_args,
)
from ska_tango_testing.integration.event import ReceivedEvent

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def is_attribute_value_valid(received_event: ReceivedEvent) -> bool:
    """This method is utilised to validate the event data received
    as part of long running command result attribute.

    Args:
        received_event (ReceivedEvent): long running command result
        attribute event data

    Returns:
        bool: Returns True if the event data is valid else False
    """
    try:
        if len(received_event.attribute_value) != 2:
            return False

        if len(json.loads(received_event.attribute_value[1])) == 2:
            result_code, message = json.loads(
                received_event.attribute_value[1]
            )
            return all(
                [isinstance(result_code, int), isinstance(message, str)]
            )
        return False
    except (AttributeError, ValueError) as exception:
        LOGGER.error("Issue with the type of event received: %s", exception)
        return False


def has_desired_result_code_message_in_lrcr_event(
    assertpy_context: Any,
    device_name: str,
    exception_messages: list[str],
    unique_id: str,
    result_code: ResultCode,
):
    """Method that verifies whether LongRunningCommandResult event has
    the desired characteristics.
    Example:
    In case of failures, we get following event
    ("1234_Command_Name","[3,'Command Failed']") or
    ("1234_Command_Name","[5,'Command Rejected']")

    To assert such failure message user can use this method accordingly
    assert_that(tracer).has_desired_result_code_message_in_lrcr_event(
        device_name= "tango_trl",
        exception_message=["Failed"],
        unique_id = "1234_Command_Name",
        result_code = ResultCode.FAILED
    )
    ("1234_Command_Name","[3,'Command Failed due to *** reason ,
    please check key ABC in json']")
    In case to check multiple data in one message user can provide multiple
    substring that is expected in the error message event.
    This helpful when the error message is long and user need to check only
    main content within it.
    assert_that(tracer).has_desired_result_code_message_in_lrcr_event(
        device_name= "tango_trl",
        exception_message=["Command Failed", "check key ABC", "due to ***"],
        unique_id = "1234_Command_Name",
        result_code = ResultCode.FAILED
    )

    Args:
        assertpy_context (Any): The assertpy context object
        (It is passed automatically).
        device_name (str | tango.DeviceName): the expected source of the LRCR
        event, expressed as a device name or a Tango device proxy instance.
        exception_messages (list[str]): The exception message list that
        we expect in the LongRunningCommandResult attribute event.
        unique_id (str): The unique id that we expect
        in the LongRunningCommandResult attribute event.
        result_code (ResultCode): The ResultCode ENUM that we expect
        in the LongRunningCommandResult attribute event.

    Returns:
        Any: the ``assertpy`` context.
    Raises:
    ValueError: If the TangoEventTracer instance is not found
        (i.e., the method is called outside an assert_that(tracer) context)

    """
    # check assertpy_context has a tracer object
    tracer = _get_tracer(assertpy_context)
    # quick trick: if device_name is a device proxy, get the name
    if isinstance(device_name, tango.DeviceProxy):
        device_name = device_name.dev_name()

    # start time is needed in case of error
    run_query_time = datetime.now()

    result = tracer.query_events(
        lambda e: e.has_device(device_name)
        and e.has_attribute("longRunningCommandResult")
        and is_attribute_value_valid(e)
        and e.attribute_value[0] == unique_id
        and json.loads(e.attribute_value[1])[0] == result_code
        and all(
            exception_message in json.loads(e.attribute_value[1])[1]
            for exception_message in exception_messages
        ),
        timeout=getattr(assertpy_context, "event_timeout", None),
    )
    if len(result) == 0:
        event_list = "\n".join([str(event) for event in tracer.events])
        msg = "Expected to find an event matching the predicate"
        if hasattr(assertpy_context, "event_timeout"):
            msg += f" within {assertpy_context.event_timeout} seconds"
        else:
            msg += " in already existing events"
        msg += ", but none was found.\n\n"
        msg += f"Events captured by TANGO_TRACER:\n{event_list}"
        msg += "\n\nTANGO_TRACER Query arguments: "
        msg += _print_passed_event_args(
            device_name,
            "longRunningCommandResult",
            (unique_id, result_code, exception_messages),
        )
        msg += "\nQuery start time: " + str(run_query_time)
        msg += "\nQuery end time: " + str(datetime.now())

        return assertpy_context.error(msg)

    return assertpy_context
