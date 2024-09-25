# This BDD test performs TMC-SDP pairwise testing to verify Abort command flow in obsStates IDLE and READY.
@XTP-29397 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: TMC executes an Abort on SDP subarray
    Given the telescope is in ON state
    And TMC and SDP subarray <subarray_id> is in <obsstate> ObsState
    When I issued the Abort command to the TMC subarray <subarray_id>
    Then the SDP subarray <subarray_id> transitions to ObsState ABORTED
    And the TMC subarray <subarray_id> transitions to ObsState ABORTED
    Examples:
    | subarray_id | obsstate |
    | 1           | IDLE     |
    | 1           | READY    |
    