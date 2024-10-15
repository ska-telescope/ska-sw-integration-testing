Feature: test Assign and Release Resources for the Mid Subarray
     This feature tests the functionality of assigning and releasing resources for the Mid subarray in 
    the telescope system. The scenarios ensure that the subarrays transition correctly between their 
    operational states

@XTP-65630 @XTP-66801 @SAHYADRI
Scenario: Assign resources to Mid subarray
    Given telescope is in ON state
    And subarray is in EMPTY ObsState
    When I assign resources to the subarray
    Then the TMC, CSP and SDP subarrays transition to RESOURCING obsState
    And the CSP, SDP and TMC subarrays must be in IDLE obsState
   
@XTP-67033 @XTP-66801 @SAHYADRI
Scenario: Release resources from Mid subarray
    Given telescope is in ON state
    And subarray is in the IDLE obsState
    When I release all resources assigned to it
    Then the TMC, CSP and SDP subarrays transition to RESOURCING obsState
    And the TMC, CSP and SDP subarrays must be in EMPTY obsState
