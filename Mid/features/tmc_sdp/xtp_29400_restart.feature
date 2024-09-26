# This BDD test performs TMC-SDP pairwise testing to verify Restart command flow.
@XTP-29400 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: TMC executes a Restart on SDP subarray when subarray completes abort
    Given the telescope is in ON state
    And TMC and SDP subarray <subarray_id> is in ABORTED ObsState
    When I command it to Restart 
    Then the SDP subarray <subarray_id> transitions to ObsState EMPTY
    And the TMC subarray <subarray_id> transitions to ObsState EMPTY
    Examples:
    | subarray_id |
    | 1           |
    