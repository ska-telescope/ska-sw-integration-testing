Feature: This feature describes abort and reset for the Low telescope subarray 
    with TMC, including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

Scenario: IDLE to ABORT - CMD Abort
    Given a Low telescope
    And telescope is in ON state
    Then subarrays is in IDLE ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState

Scenario: READY to ABORT - CMD Abort
    Given a Low telescope
    And telescope is in ON state
    Then subarrays is in READY ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsStat

Scenario: SCANNING to ABORT - CMD Abort
    Given a Low telescope
    And telescope is in ON state
    Then subarrays is in SCANNING ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState


Scenario: TMC validates Abort Command in intermediate obsState
    Given a Low telescope
    And telescope is in ON state
    Given a Subarray in intermediate obsState <obs_state>
    When I Abort it
    Then the Subarray transitions to ABORTED obsState

    Examples:
    | obs_state         |
    | RESOURCING        |
    | CONFIGURING       |