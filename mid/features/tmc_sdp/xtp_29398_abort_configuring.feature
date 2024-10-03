# This BDD test performs TMC-SDP pairwise testing to verify Abort command flow in obsState CONFIGURING.
@XTP-29398 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: Abort configuring SDP using TMC
    Given TMC subarray <subarray_id> and SDP subarray <subarray_id> busy configuring
    When I command it to Abort
    Then the SDP subarray <subarray_id> transitions to ObsState ABORTED
    And the TMC subarray <subarray_id> transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |
        