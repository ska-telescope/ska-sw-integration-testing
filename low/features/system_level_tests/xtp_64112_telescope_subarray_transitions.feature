Feature: This feature describes assigning, releasing, and configuring resources for the Low telescope subarray 
    with TMC, including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

    @XTP-65635 @XTP-64112 @TEAM_HIMALAYA
    Scenario: Assign resources to Low subarray
        Given a Low telescope
        And telescope is in ON state
        And subarray is in EMPTY ObsState
        When I assign resources to the subarray
        Then the TMC, CSP, SDP, and MCCS subarrays transition to RESOURCING obsState
        And the TMC, CSP, SDP, and MCCS subarrays transition to IDLE obsState

    @XTP-65636 @XTP-64112 @TEAM_HIMALAYA
    Scenario: Release resources from Low subarray
        Given a Low telescope
        And telescope is in ON state
        And subarray is in the IDLE obsState
        When I release all resources assigned to it
        Then the TMC, CSP, SDP, and MCCS subarrays must be in EMPTY obsState

    @XTP-66007 @XTP-64112
    Scenario: Configure the Low telescope subarray using TMC
        Given a Low telescope
        And telescope is in ON state
        And subarray is in IDLE ObsState
        When I configure it for a scan
        Then the TMC, CSP, SDP, and MCCS subarrays transition to CONFIGURING obsState
        And the TMC, CSP, SDP, and MCCS subarrays transition to READY obsState
  
    @XTP-66037 @XTP-64112
    Scenario: End Configuration to the Low telescope subarray using TMC
        Given a Low telescope
        And telescope is in ON state
        And subarray is in READY ObsState
        When I end the configuration
        Then the TMC, CSP, SDP, and MCCS subarrays transition to IDLE obsState
