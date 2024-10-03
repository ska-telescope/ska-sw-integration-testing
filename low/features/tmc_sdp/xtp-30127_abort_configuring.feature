@XTP-30127 @XTP-29227 @tmc_sdp
Scenario: Use TMC command Abort to trigger SDP subarray transition from ObsState CONFIGURING to ObsState ABORTED
    Given TMC subarray <subarray_id> and SDP subarray <subarray_id> busy configuring
    When I command it to Abort
    Then the SDP subarray transitions to ObsState ABORTED
    And the subarray transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |