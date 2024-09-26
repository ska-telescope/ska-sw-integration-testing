# This BDD test performs TMC-SDP pairwise testing to verify ReleaseResources command flow.
@XTP-29294 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: Release resources from SDP Subarray using TMC
    Given a TMC and SDP
    And a subarray <subarray_id> in the IDLE obsState
    When I release all resources assigned to subarray <subarray_id>
    Then the SDP subarray <subarray_id> must be in EMPTY obsState
    And TMC subarray <subarray_id> obsState transitions to EMPTY
    Examples:
        | subarray_id |
        | 1           |
        