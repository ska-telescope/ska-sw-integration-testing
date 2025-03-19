Feature: This feature describes abort and reset for the Low telescope subarray 
    with TMC, including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

Scenario: TMC validates Abort Command
    Given a Low telescope
    And telescope is in ON state
    Then subarray is in <obs_state> ObsState
    When I Abort it
    Then the TMC, CSP, SDP, and MCCS subarrays transitions to ABORTED obsState

    Examples:
    | obs_state   |
    | IDLE        |
    | READY       |
