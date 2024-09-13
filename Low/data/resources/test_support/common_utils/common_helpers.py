"""Common helpers for ska-tmc-low-integration """
import logging
import signal
import threading
from time import sleep

from numpy import ndarray
from ska_ser_logging import configure_logging

# SUT frameworks
from tango import CmdArgType, DeviceProxy, EventType

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class Resource:
    """Resources class for common helpers"""

    device_name = None

    def __init__(self, device_name):
        self.device_name = device_name

    def get(self, attr):
        """Method for getting attributes"""
        device_proxy = DeviceProxy(self.device_name)
        # Set timeout to 5 sec.
        # Sometimes read attribute timeout with default 3 sec time
        device_proxy.set_timeout_millis(5000)
        attrs = device_proxy.get_attribute_list()
        if attr not in attrs:
            return "attribute not found"
        # pylint: disable=protected-access
        attr_data_type = device_proxy._get_attribute_config(attr).data_type
        if attr_data_type == CmdArgType.DevEnum:
            return getattr(device_proxy, attr).name
        if attr_data_type == CmdArgType.DevState:
            return str(device_proxy.read_attribute(attr).value)

        value = getattr(device_proxy, attr)
        if isinstance(value, ndarray):
            return tuple(value)
        return getattr(device_proxy, attr)

    def assert_attribute(self, attr):
        """Method for asserting"""
        return ObjectComparison(f"{self.device_name}.{attr}", self.get(attr))


class ObjectComparison:
    """Class for comparing values"""

    def __init__(self, obj, value):
        self.value = value
        self.object = obj

    def equals(self, value):
        """Checks is the values provided equals to class value"""
        try:
            if isinstance(value, list):
                # a list is assumed to mean an or condition, a tuple is
                # assumed to be  an and condition
                assert self.value in value
            else:
                assert self.value == value
        # pylint: disable=broad-exception-caught
        except Exception as ex:
            # pylint: disable=broad-exception-raised
            raise Exception(
                f"{self.object} is asserted \
                    to be {value} but was instead {self.value} {ex}"
            ) from ex

    def not_equals(self, value):
        """Checks is the values provided is not equals to class value"""
        try:
            if isinstance(value, list):
                # a list is assumed to mean an or condition, a tuple is
                # assumed to be  an and condition
                assert self.value not in value
            else:
                assert self.value != value
        # pylint: disable= broad-exception-caught
        except Exception as ex:
            # pylint: disable=broad-exception-raised
            raise Exception(
                f"{self.object} is asserted \
                    to be {value} but was instead {self.value} {ex}"
            ) from ex


# time keepers based on above resources
class Monitor:
    """
    Monitors an attribute of a given resource and allows a user to block/wait
    on a specific condition:
    1. the attribute has changed in value (but it can be any value):
        previous value != current value
    2. the attribute has changed in value and to a specific desired value:
        previous value = future value but have changed also
    3. the attribute has changed or is already the desired value:
        previous value = future value
    4. instead of a direct equality a predicate can also be used to perform
    the comparison The value for which it must wait can also be provided by
    the time at calling the wait or by the time of instantiation
    The former allows for the monitor to be used in a list that waits
    iteratively, the latter is when it is inline at where it should wait
    """

    previous_value = None
    resource = None
    attr = None
    device_name = None
    current_value = None

    def __init__(
        self,
        resource,
        previous_value,
        attr,
        future_value=None,
        predicate=None,
        require_transition=False,
    ):
        self.previous_value = previous_value
        self.resource = resource
        self.attr = attr
        self.require_transition = require_transition
        self.future_value = future_value
        self.device_name = resource.device_name
        self.current_value = previous_value
        self.data_ready = False
        self.predicate = predicate

    def _update(self):
        """updates the current value of attribute"""
        self.current_value = self.resource.get(self.attr)

    def _conditions_not_met(self):
        """Change comparison section (only if require_transition)"""
        if self.require_transition:
            is_changed_comparison = self.previous_value != self.current_value
            if isinstance(is_changed_comparison, ndarray):
                is_changed_comparison = is_changed_comparison.all()
            if is_changed_comparison:
                self.data_ready = True
        else:
            self.data_ready = True
        # comparison with future section (only if future value given)
        # if no future value was given it means you can ignore (or set to true)
        # comparison with a future
        if self.future_value is None:
            is_eq_to_future_comparison = True
        else:
            if self.predicate is None:
                is_eq_to_future_comparison = (
                    self.current_value == self.future_value
                )
            else:
                is_eq_to_future_comparison = self.predicate(
                    self.current_value, self.future_value
                )
            if isinstance(is_eq_to_future_comparison, ndarray):
                is_eq_to_future_comparison = is_eq_to_future_comparison.all()
        return (not self.data_ready) or (not is_eq_to_future_comparison)

    def _compare(self, desired):
        """Compare the current value with desired value"""
        comparison = self.current_value == desired
        if isinstance(comparison, ndarray):
            return comparison.all()
        return comparison

    def _wait(self, timeout: int = 80, resolution: float = 0.1):
        """Wait method for monitor class"""
        count_down = timeout
        while self._conditions_not_met():
            count_down -= 1
            if count_down == 0:
                future_shim = ""
                if self.future_value is not None:
                    future_shim = f" to {self.future_value}"
                # pylint: disable= broad-exception-raised
                raise Exception(
                    f"Timed out waiting \
                        for {self.resource.device_name}.{self.attr} to\
                        change from {self.previous_value}{future_shim} in\
                        {timeout * resolution}s (current val\
                        = {self.current_value})"
                )
            sleep(resolution)
            self._update()
        return count_down

    def get_value_when_changed(self, timeout: int = 50):
        """Returns value when it gets changed"""
        response = self._wait(timeout)
        if response == "timeout":
            return "timeout"
        return self.current_value

    def wait_until_conditions_met(self, timeout: int = 50):
        """Waits until conditions is satisfies"""
        return self._wait(timeout)

    def wait_until_value_changed(self, timeout=50):
        """Waits until values changed"""
        return self._wait(timeout)

    def wait_until_value_changed_to(
        self, value, timeout: int = 50, resolution: float = 0.1
    ):
        """Waits until the values changed to given value"""
        count_down = timeout
        self._update()
        while not self._compare(value):
            count_down -= 1
            if count_down == 0:
                # pylint: disable= broad-exception-raised
                raise Exception(
                    f"Timed out waiting\
                          for {self.resource.device_name}.{self.attr} to\
                              change from {self.current_value} to {value} in\
                                  {timeout * resolution}s"
                )
            sleep(resolution)
            self._update()
        return count_down


class Subscriber:
    """Subscriber class for events"""

    def __init__(self, resource, implementation="polling"):
        self.resource = resource
        self.implementation = implementation

    def for_a_change_on(self, attr, changed_to=None, predicate=None):
        """Method for changing attribute"""
        if self.implementation == "polling":
            value_now = self.resource.get(attr)
            return Monitor(
                self.resource,
                value_now,
                attr,
                changed_to,
                predicate,
                require_transition=True,
            )
        if self.implementation == "tango_events":
            return AttributeWatcher(
                self.resource,
                attr,
                desired=changed_to,
                predicate=predicate,
                require_transition=True,
                start_now=True,
            )
        return None

    def to_become(self, attr, changed_to, predicate=None):
        """To monitor the attribute value against changed_to_value"""
        if self.implementation == "polling":
            value_now = self.resource.get(attr)
            return Monitor(
                self.resource,
                value_now,
                attr,
                changed_to,
                predicate,
                require_transition=False,
            )
        if self.implementation == "tango_events":
            return AttributeWatcher(
                self.resource,
                attr,
                desired=changed_to,
                predicate=predicate,
                require_transition=False,
                start_now=True,
            )
        return None

    def for_any_change_on(self, attr, predicate=None):
        """To monitor changes for attribute"""
        if self.implementation == "polling":
            value_now = self.resource.get(attr)
            return Monitor(
                self.resource, value_now, attr, require_transition=True
            )
        if self.implementation == "tango_events":
            return AttributeWatcher(
                self.resource,
                attr,
                desired=None,
                predicate=predicate,
                require_transition=True,
                start_now=True,
            )
        return None


def watch(resource, implementation="polling"):
    """Returns subscriber class object
    and monitors resources"""
    return Subscriber(resource, implementation)


# this is a composite type of waiting based on a set of predefined
# pre conditions expected to be true
class Waiter:
    """Waiter class for delays on predefined conditions"""

    def __init__(self, **kwargs):
        """
        Args:
            kwargs (dict): device names
        """
        self.waits = []
        self.logs = ""
        self.error_logs = ""
        self.timed_out = False
        self.sdp_subarray1 = kwargs.get("sdp_subarray")
        self.sdp_master = kwargs.get("sdp_master")
        self.csp_subarray1 = kwargs.get("csp_subarray")
        self.csp_master = kwargs.get("csp_master")
        self.tmc_subarraynode1 = kwargs.get("tmc_subarraynode")
        self.tmc_csp_subarray_leaf_node = kwargs.get(
            "tmc_csp_subarray_leaf_node"
        )

    def clear_watches(self):
        """Resets the waits list"""
        self.waits = []

    def set_wait_for_going_to_off(self):
        """Sets waits for turning off the telescope"""
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_master)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_master)).to_become(
                "State", changed_to="OFF"
            )
        )

    def set_wait_for_going_to_standby(self):
        """Sets waits for turning the devices to standby mode"""
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_master)).to_become(
                "State", changed_to="STANDBY"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "State", changed_to="OFF"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_master)).to_become(
                "State", changed_to="STANDBY"
            )
        )

    def set_wait_for_telescope_on(self):
        """Sets waits for turning the devices in ON state"""
        self.waits.append(
            watch(Resource(self.sdp_master)).to_become(
                "State", changed_to="ON"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "State", changed_to="ON"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_master)).to_become(
                "State", changed_to="ON"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "State", changed_to="ON"
            )
        )

    def set_wait_for_going_to_empty(self):
        """Sets wait for devices to change the obstate to EMPTY"""
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="EMPTY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "assignedResources", changed_to=None
            )
        )

    def set_wait_for_assign_resources(self):
        """Sets wait for device to execute assign resources"""
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )

        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )

    def set_wait_for_configuring(self):
        """Sets wait for obsstate to change to configuring"""
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="CONFIGURING"
            )
        )

    def set_wait_for_obs_state(self, obs_state=None):
        """Sets wait for obsstate"""
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to=obs_state
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to=obs_state
            )
        )

        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to=obs_state
            )
        )

    def set_wait_for_configure(self):
        """Sets wait for device to execute configure command"""
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )

        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="READY"
            )
        )

    def set_wait_for_idle(self):
        """Sets wait for obsstate to change to IDLE"""
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="IDLE"
            )
        )

    def set_wait_for_aborted(self):
        """Sets wait for obsstate to change to ABORTED"""
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="ABORTED"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="ABORTED"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="ABORTED"
            )
        )

    def set_wait_for_ready(self):
        """Sets wait for obsstate to change to READY"""
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="READY"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="READY"
            )
        )

    def set_wait_for_specific_obsstate(self, obsstate: str, devices: list):
        """Waits for the obsState of given devices
        to change to specified value."""
        for device in devices:
            self.waits.append(
                watch(Resource(device)).to_become(
                    "obsState", changed_to=obsstate
                )
            )

    def set_wait_for_long_running_command_result(
        self, command_result: str, devices: list
    ):
        """Waits for the longRunningCommandResult event of given devices"""
        for device in devices:
            self.waits.append(
                watch(Resource(device)).to_become(
                    "longRunningCommandResult", changed_to=command_result
                )
            )

    def set_wait_for_scanning(self):
        """Sets wait for obsstate to change to SCANNING"""
        self.waits.append(
            watch(Resource(self.csp_subarray1)).to_become(
                "obsState", changed_to="SCANNING"
            )
        )
        self.waits.append(
            watch(Resource(self.sdp_subarray1)).to_become(
                "obsState", changed_to="SCANNING"
            )
        )
        self.waits.append(
            watch(Resource(self.tmc_subarraynode1)).to_become(
                "obsState", changed_to="SCANNING"
            )
        )

    def set_wait_for_delayvalue(self):
        """Sets wait for value in delayModel attribute"""
        Resource(self.tmc_csp_subarray_leaf_node).assert_attribute(
            "delayModel"
        ).not_equals([""])

    def wait(self, timeout: int = 30, resolution: float = 0.1):
        """Delay method subscriber class"""
        self.logs = ""
        while self.waits:
            wait = self.waits.pop()
            if isinstance(wait, AttributeWatcher):
                timeout = timeout * resolution
            try:
                result = wait.wait_until_conditions_met(timeout=timeout)
            # pylint: disable= broad-exception-caught
            except Exception as ex:
                self.timed_out = True
                future_value_shim = ""
                timeout_shim = timeout * resolution
                if isinstance(wait, AttributeWatcher):
                    timeout_shim = timeout
                if wait.future_value is not None:
                    future_value_shim = f" to {wait.future_value} \
                        (current val={wait.current_value})"
                self.error_logs += f"{wait.device_name} timed\
                      out whilst waiting for {wait.attr} to\
                      change from\
                      {wait.previous_value}{future_value_shim} in\
                      {timeout_shim:f}s and raised\
                      {ex}\n"

            else:
                timeout_shim = (timeout - result) * resolution
                if isinstance(wait, AttributeWatcher):
                    timeout_shim = result
                self.logs += f"{wait.device_name} changed\
                          {wait.attr} from {wait.previous_value} to\
                            {wait.current_value} after\
                                  {timeout_shim:.2f}s \n"
        if self.timed_out:
            # pylint: disable= broad-exception-raised
            raise Exception(
                f"timed out, the following\
                      timeouts occurred:\n{self.error_logs}\
                          Successful changes:\n{self.logs}"
            )


class WaitForScan(Waiter):
    """Waits for scan command"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sdp_subarray1 = kwargs.get("sdp_subarray")
        self.csp_subarray1 = kwargs.get("csp_subarray")
        self.tmc_subarraynode1 = kwargs.get("tmc_subarraynode")
        self.tmc_subarraynode = watch(
            Resource(kwargs.get("tmc_subarraynode"))
        ).for_a_change_on("obsState")
        self.csp_subarray = watch(
            Resource(kwargs.get("csp_subarray"))
        ).for_a_change_on("obsState")
        self.sdp_subarray = watch(
            Resource(kwargs.get("sdp_subarray"))
        ).for_a_change_on("obsState")

    # pylint:disable=arguments-differ
    def wait(self, timeout):
        """Delay method for waitForScan class"""
        logging.info(
            "scan command dispatched, checking that the state transitioned to \
                SCANNING"
        )
        self.tmc_subarraynode.wait_until_value_changed_to("SCANNING", timeout)
        self.csp_subarray.wait_until_value_changed_to("SCANNING", timeout)
        self.sdp_subarray.wait_until_value_changed_to("SCANNING", timeout)
        logging.info(
            "state transitioned to SCANNING, waiting for it to return to READY"
        )
        self.tmc_subarraynode.wait_until_value_changed_to("READY", timeout)
        self.csp_subarray.wait_until_value_changed_to("READY", timeout)
        self.sdp_subarray.wait_until_value_changed_to("READY", timeout)


# Waiters based on tango DeviceProxy's ability to subscribe to events
class AttributeWatcher:
    """Listens to events in a device and enables waiting until a predicate is
    true or publish to a subscriber
    It allows in essence for the ability to wait for three types of conditions:
    1. The attribute value has become or was already from the start the desired
     future value
    2. The attribute value has changed from its original value into any new
    value
    3. The attribute value as transitioned into the desired future value
    (this means it must have changed from the original)
    These different conditions upon which to wait is specified by the
    constructure params. However the typical use case is to use
    the "watch.for_a... factory methods to instantiate the watcher
    (see subscriber).This is also the same type of watch as implemented by

    the monitor class except that this one uses the tango device subscribe
    mechanism as opposed to a simple polling implemented by the other.
    Thus the key mechanism is a call back with the appropriate event pushed
    by the device, the event in turns gets evaluated against the required
    conditions to determine whether a threading  event should be set (in case
    of all conditions being met.) This allows a wait method to hook on the
    event by calling the wait method (see python threading event)
    """

    def __init__(
        self,
        resource,
        attribute,
        desired=None,
        predicate=None,
        require_transition=False,
        start_now=True,
        polling=100,
    ):
        self.device_proxy = DeviceProxy(resource.device_name)
        self.device_name = resource.device_name
        self.future_value = desired
        self.polling = polling
        self.attribute = attribute
        self.attr = attribute
        self.previous_value = None
        self.current_value = None
        self.is_changed = False
        self.require_transition = require_transition
        self.result_available = threading.Event()
        self.current_subscription = None
        self.original_polling = None
        self.waiting = False
        self.start_time: float = 0.0
        self.elapsed_time: float = 0.0
        self.timeout: int = 0
        self.desired = None
        self._waiting: bool = False
        if predicate is None:
            self.predicate = self._default_predicate
        else:
            self.predicate = predicate
        if start_now:
            self.start_listening()

    def _default_predicate(self, current_value, desired):
        """Default comparator method for attribute watcher class"""
        comparison = current_value == desired
        if isinstance(comparison, ndarray):
            return comparison.all()
        return comparison

    def start_listening(self):
        """This method start to monitor the attributes"""
        if self.device_proxy.is_attribute_polled(self.attribute):
            # must be reset to original when finished
            self.original_polling = self.device_proxy.get_attribute_poll_period
        self.device_proxy.poll_attribute(self.attribute, self.polling)
        self.current_subscription = self.device_proxy.subscribe_event(
            self.attribute, EventType.CHANGE_EVENT, self._cb
        )

    def _cb(self, event):
        """This method will be called by a thread"""
        self.current_value = str(event.attr_value.value)
        if self.previous_value is None:
            # this implies it is the first event and is always treated as the
            # value when subscription started
            self.previous_value = self.current_value
            self.start_time = event.reception_date.totime()
        if not self.is_changed:
            self.is_changed = self.current_value != self.previous_value
        if self.future_value is None:
            # this means that it is only evaluating a change and not the end
            # result of the evaluation
            if self.is_changed:
                self.elapsed_time = (
                    event.reception_date.totime() - self.start_time
                )
                self.result_available.set()
        elif self.predicate(self.current_value, self.future_value):
            if self.require_transition:
                if self.is_changed:
                    self.elapsed_time = (
                        event.reception_date.totime() - self.start_time
                    )
                    self.result_available.set()
            else:
                self.elapsed_time = (
                    event.reception_date.totime() - self.start_time
                )
                self.result_available.set()

    def _handle_timeout(self):
        """This method handles timeout"""
        self.stop_listening()
        # pylint: disable= broad-exception-raised
        raise Exception(
            f"Timed out waiting for an change on {self.device_proxy.name()}.\
            {self.attribute} to change from {self.previous_value} to \
            {self.desired} in {self.timeout}s (current value is \
            {self.current_value}"
        )

    def _wait(self, timeout):
        """Delay method for attributeWather class"""
        self.timeout = timeout
        signal.signal(signal.SIGALRM, self._handle_timeout)
        signal.alarm(timeout)
        self.result_available.wait()
        signal.signal(0)
        self.stop_listening()

    def stop_listening(self):
        """Stops polling for current attribute"""
        if self.original_polling is not None:
            self.device_proxy.poll_attribute(self.original_polling)
        self.device_proxy.unsubscribe_event(self.current_subscription)

    def wait_until_value_changed_to(self, desired, timeout: int = 2):
        """Waits for value changed to desired value"""
        self.desired = desired
        self.waiting = True
        self._wait(int(timeout))
        return self.elapsed_time

    def wait_until_conditions_met(self, timeout: int = 2):
        """Waits until conditions is satisfied"""
        self._waiting = True
        self._wait(int(timeout))
        return self.elapsed_time
