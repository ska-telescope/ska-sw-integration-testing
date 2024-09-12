"""Implement Event checker class which can be used to validate events
"""
import logging
import os
import time
from typing import Any

from ska_ser_logging import configure_logging
from ska_tango_testing.mock.tango.event_callback import (
    MockTangoEventCallbackGroup,
)
from tango import AttributeProxy, EventType

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class AttributeNotSubscribed(Exception):
    # Raise this exception when attribute is not subscribed
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EventRecorder(object):
    """Implement method required for validating events"""

    def __init__(self):
        """Initialize events data"""
        self.subscribed_events = {}
        self.subscribed_devices = []

    def subscribe_event(
        self, device: Any, attribute_name: str, timeout: float = 100.0
    ):
        """Subscribe for change event for given attribute
        Args:
            device: Tango Device Proxy Object
            attribute_name (str): Name of the attribute
            timeout (float): number of seconds to wait for the callable to be
            called
        """
        callable_name = self._generate_callable_name(device, attribute_name)
        attribute_change_event_callback = MockTangoEventCallbackGroup(
            callable_name,
            timeout=timeout,
        )

        # This approach ensures that the subscription to the event is
        # attempted multiple times if it fails initially due to transient
        # issues, while also logging any persistent issues that might
        # require further investigation. Adjustments can be made to the
        # wait time (time.sleep(...))
        # based on specific requirements or characteristics of the
        # environment in which the code runs.

        start_time = time.time()
        TIMEOUT = 30

        while time.time() - start_time < TIMEOUT:
            try:
                event_id = device.subscribe_event(
                    attribute_name,
                    EventType.CHANGE_EVENT,
                    attribute_change_event_callback[callable_name],
                )
                break

            except Exception:
                time.sleep(1)
        else:
            LOGGER.info(
                "Timeout of %d seconds reached - %s", TIMEOUT, Exception
            )
            raise Exception

        # ----------------------------------------------------------

        self.subscribed_devices.append((device, event_id))

        if callable_name not in self.subscribed_events:
            LOGGER.info(f"{callable_name} is subscribed for {attribute_name}")
            self.subscribed_events[
                callable_name
            ] = attribute_change_event_callback

    def has_change_event_occurred(
        self,
        device: Any,
        attribute_name: str,
        attribute_value: Any,
        lookahead: int = 7,
    ) -> bool:
        """Validate Change Event occurred for provided attribute
        This method check attribute value changed within number of lookahead
        events
        Args:
            device: Tango Device Proxy Object
            attribute_name (str): Name of the attribute
            attribute_value : Value of attribute
        Returns:
            bool: Change Event occurred True or False
        """
        callable_name = self._generate_callable_name(device, attribute_name)
        change_event_callback = self.subscribed_events.get(callable_name, None)
        if change_event_callback:
            try:
                return change_event_callback[
                    callable_name
                ].assert_change_event(attribute_value, lookahead=lookahead)
            except AssertionError:
                device_name = device.dev_name()
                dish_prefix = ""
                real_dish1_fqdn = os.getenv("DISH_NAME_1")
                if ("dish-manager" in device_name) and (
                    "dish-lmc-1" not in real_dish1_fqdn
                ):
                    # It is a real dish device therefore need a full FQDN
                    # for dish
                    dish_prefix = real_dish1_fqdn.replace(
                        "mid-dish/dish-manager/SKA001", ""
                    )
                    dish_number = "".join(
                        letter for letter in device_name if letter.isdigit()
                    )
                    dish_prefix = dish_prefix.replace("001", dish_number)

                LOGGER.info("dish_prefix: %s", dish_prefix)
                full_attr_name = (
                    dish_prefix + device_name + "/" + attribute_name
                )
                attr_proxy = AttributeProxy(full_attr_name)
                attr_value = attr_proxy.read().value
                if attr_value == attribute_value:
                    return True
                return False

        raise AttributeNotSubscribed(
            f"Attribute {callable_name} is not subscribed"
        )

    def clear_events(self):
        """Clear Subscribed Events"""
        for device, event_id in self.subscribed_devices:
            try:
                device.unsubscribe_event(event_id)
            except KeyError:
                # If event id is not subscribed then Key Error is raised
                pass
        self.subscribed_devices = []
        self.subscribed_events = {}

    def _generate_callable_name(self, device: Any, attribute_name: str):
        """Generate callable name based on device name and attribute name"""
        return f"{device.name()}_{attribute_name}"
