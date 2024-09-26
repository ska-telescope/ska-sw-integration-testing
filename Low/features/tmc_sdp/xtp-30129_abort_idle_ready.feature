@XTP-30129 @XTP-29227 @tmc_sdp
Scenario: Use TMC command Abort to trigger SDP subarray transition from ObsStates IDLE and READY to ObsState ABORTED
    Given TMC subarray <subarray_id> and SDP subarray <subarray_id> in ObsState <obsstate>
    When I command it to Abort
    Then the SDP subarray transitions to ObsState ABORTED
    And the subarray transitions to ObsState ABORTED
    Examples:
    | subarray_id | obsstate |
    | 1           | IDLE     |
    | 1           | READY    |