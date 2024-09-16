All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----
[0.22.2]
************
*Read the Docs warnings addressed*


[0.22.1]
************
*Observation State Aggregation Logic improvements*
  * Rule engine is used to define rules for ObsState
  * EventDataStorage class introduced to store event related data

[0.22.0]
************
* Utilised base class v1.0.0 and pytango 9.5.0 on TMC nodes
    * Utilised ska-tmc-common v0.17.6 for tango helper devices
    * Implemented queue according to support base classes v1.0.0
    * Refactored command allowed method to put commands in queue
    * Implemented command allowed methods for observation specific commands to allow/reject the queued  task, ResultCode.NOT_ALLOWED/ResultCode.REJECTED
    * Refactored error propogation implementation on SubarrayNode, CentralNode and tmc leaf nodes to handle longrunningcommandresult attribute new format in case of raised exceptions
    * Refactored error propogation implementation to handle longrunningcommandresult event for ResultCode.NOT_ALLOWED, ResultCode.REJECTED and ResultCode.FAILED
    * Refactored all the integration tests(pairwise and with mocks) for TMC Mid according to longrunningcommandresult attribute value

* Utilised cspsubarrayleafnode v0.19.1 with fixed SKB-413: Mid Delay Model code pointing to wrong dishes
    * Implemented antenna parameters objects to generate according to mid_json layout
    * Corrected Mid Delay Model to point to SKA or MKT dish according to assigned receptors

* Utilise dishleafnode: 0.16.3 Patch release for SKB-419 fix from branch SAH-1566

[0.21.2]
************
* Fix image link reference for DishLeafNode

[0.21.1]
************
* Resolve SKB-419
* Resolve SKB-384 -  Currently, across all devices in TMC, there are no polled attributes (after our work on skb-384). TMC monitors the attributes of other devices using event subscription methods. Unlike polling, which involves continuous querying, event subscription relies on a push-based mechanism. When a device generates an event (such as an attribute value change), the Tango system notifies all subscribed clients. As a result, there is no ongoing polling loop; TMC only receives updates when events occur."
* Note: This release - REL-1623 is from SAH-1564.

[0.21.0]
************
* Improvement as per ADR-76 changes are done in Dish Leaf node and Subarray Node.
* Enabled ProgramTrackTable.
* Fixed CORBA issues in dish leaf node while execution of commands.

[0.20.1]
************
* Integrate TMC-Dish Scan functionality implementation
* This release is from branch sah-1524

[0.20.0]
************
* SP-4028 Delay Model Improvements
* SKB-329 and SKB-330 bug fixes on CspSubarrayLeafNode(v0.16.2)
* Updated affected BDD test case - XTP-32140

[0.19.2]
***********
* Updated Subarray Node to v0.18.0 that resolves the SKB-331 and gets rid of hardcoded interface values
* Fix bug SKB-337
* Updated the kValue range to 1 to 1177.
* kValue range is a device property
* Configure command gets accepted if the kvalue for assinged dishes are either all same or all different

[0.19.1]
************
* Intermediate chart with TMC updates to work with dish-lmc chart 3.0.0
* Fixed issues in the tests

[0.19.0]
************
* Aligned delay model json as per ADR-88
* DelayCadence, DelayValidity and DelayAdvancedTime values are configurable
* Fixed SKB-300

[0.18.0]
************
* Integrated ska-tmc-dishleafnode with program track table into ska-tmc-mid-integration(SP-3987)