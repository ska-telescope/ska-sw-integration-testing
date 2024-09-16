"""Implement Event checker class which can be used to validate events
"""
import logging
from typing import Any

from ska_ser_logging import configure_logging
from ska_tango_testing.mock.tango.event_callback import (
    MockTangoEventCallbackGroup,
)
from tango import EventType

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
        self, device: Any, attribute_name: str, timeout: float = 300.0
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
        event_id = device.subscribe_event(
            attribute_name,
            EventType.CHANGE_EVENT,
            attribute_change_event_callback[callable_name],
        )
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
