Feature: test Scan and EndScan commands flow for the Mid Subarray
    This feature tests the functionality of Scan and EndScan for the Mid subarray in 
    the telescope system. The scenarios ensure that the subarrays transition correctly between their 
    operational states

    @XTP-68819 @XTP-66801 @TEAM_SAHYADRI
    Scenario: Execute Scan on the Mid telescope
        Given a Mid telescope
        And a Telescope consisting of SDP, CSP and DISH that is ON
        And subarray is in the READY obsState
        When I issue the Scan command to subarray
        And the DishMaster transitions to dishMode OPERATE and pointingState TRACK   
        Then the TMC, CSP and SDP subarrays transition to SCANNING obsState
        And subarrays transitions to obsState READY once the scan duration is elapsed

    @XTP-68822 @XTP-66801 @TEAM_SAHYADRI
    Scenario: Executes EndScan command on Mid telescope
        Given a Mid telescope
        And a Telescope consisting of SDP, CSP and DISH that is ON
        And subarray is in Scanning ObsState
        When I issue the EndScan command to the subarray 
        And the DishMaster transitions to dishMode OPERATE and pointingState TRACK  
        Then the TMC, CSP and SDP subarrays transition to ObsState READY
        And the DishMaster transitions to pointingState READY