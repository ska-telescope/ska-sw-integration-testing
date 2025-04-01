Feature: This feature describes abort and restart for the Low telescope subarray 
    with TMC, including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

@XTP-78118 @XTP-64112
Scenario: IDLE to ABORT - CMD Abort
    Given a Low telescope
    And telescope is in ON state
    And subarrays is in IDLE ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState

    Examples:
    | obs_state   |
    | IDLE        |
    | READY       |
    | SCANNING    |


@XTP-78120 @XTP-64112
Scenario: READY to ABORT - CMD Abort
    Given a Low telescope
    And telescope is in ON state
    And subarrays is in READY ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState

@XTP-78121 @XTP-64112
Scenario: SCANNING to ABORT - CMD Abort
    Given a Low telescope
    And telescope is in ON state
    And subarrays is in SCANNING ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState

@XTP-78123 @XTP-64112
Scenario: RESOURCING to ABORT -CMD Abort
    Given a Low telescope
    And telescope is in ON state
    And subarrays is in RESOURCING ObsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState

@XTP-78122 @XTP-64112
Scenario: CONFIGURING to ABORT -CMD Abort
    Given a Low telescope
    And telescope is in ON state
    And subarrays is in CONFIGURING obsState
    When I Abort it
    Then the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState