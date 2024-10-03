Feature: TMC performs End Configuration on MCCS subsystem
@XTP-31010 @XTP-30488 @Team_HIMALAYA @tmc_mccs
Scenario: End configure from MCCS Subarray
    Given the Telescope is in the ON state
    And obsState of subarray <subarray_id> is READY
    When I issue the End command to the TMC subarray with the <subarray_id>
    Then the MCCS subarray is transitioned to IDLE obsState
    And TMC subarray is transitioned to IDLE obsState
    Examples:
    | subarray_id   |
    |  1            |