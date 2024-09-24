@XTP-31005 @XTP-30488 @tmc_mccs @Team_HIMALAYA
Scenario: TMC executes a EndScan command on MCCS subarray
    Given the Telescope is in ON state
    And the obsState of TMC subarray is Scanning
    When I issue the Endscan command to the TMC subarray with the <subarray_id>
    Then the MCCS subarray is transitioned to ObsState READY
    And the TMC subarray is transitioned to ObsState READY
    Examples:
    | subarray_id |
    | 1           |
