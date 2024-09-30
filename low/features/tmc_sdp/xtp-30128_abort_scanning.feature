@XTP-30128 @XTP-29227 @tmc_sdp
Scenario: Use TMC command Abort to trigger SDP subarray transition from ObsState SCANNING to ObsState ABORTED
    Given TMC subarray <subarray_id> and SDP subarray <subarray_id> busy SCANNING
    When I command it to Abort
    Then the SDP subarray transitions to ObsState ABORTED
    And the subarray transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |
