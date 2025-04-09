Feature: This feature describes abort for the Low telescope subarray, 
    including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

@XTP-78118 @XTP-64112
Scenario: Validates Abort Command
    Given a Low telescope
    And telescope is in ON state
    And subarray is in <obs_state> ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState

    Examples:
    | obs_state   |
    | IDLE        |
    | READY       |
    | SCANNING    |
    | RESOURCING  |
    | CONFIGURING |