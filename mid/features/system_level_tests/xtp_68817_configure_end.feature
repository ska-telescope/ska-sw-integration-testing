Feature: test Configure and End commands flow for the Mid Subarray
    This feature tests the functionality of Configure and End for the Mid subarray in 
    the telescope system. The scenarios ensure that the subarrays transition correctly between their 
    operational states

    @XTP-68817 @XTP-66801 @TEAM_SAHYADRI
    Scenario: Configure a Mid telescope subarray for a scan using TMC
        Given a Mid telescope
        And a Telescope consisting of SDP, CSP and DISH that is ON
        And TMC subarray in ObsState IDLE
        When I issue the Configure command to subarray
        Then the Telescope consisting of SDP and CSP devices transition to READY obsState
        And the DishMaster transitions to dishMode OPERATE and pointingState TRACK
        And CSP subarray leaf node starts generating delay values
        And SDP subarray scanType reflects correctly configured <scan_type>
        Examples:
            |    scan_type    |
            |    target:a     |

    @XTP-68818 @XTP-66801 @TEAM_SAHYADRI
    Scenario: End command on Mid telescope
        Given a Mid telescope
        And a Telescope consisting of SDP, CSP and DISH that is ON
        And subarray is in READY ObsState
        When I issue the End command to subarray 
        Then the Telescope consisting of SDP and CSP devices transition to IDLE obsState
        And the DishMaster transitions to pointingState READY

    