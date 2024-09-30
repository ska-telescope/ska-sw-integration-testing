@XTP-31001 @XTP-30488 @tmc_mccs @Team_HIMALAYA
Scenario: TMC executes a scan on MCCS subarray
    Given the Telescope is in the ON state
    And the obsState of TMC subarray is READY
    When I issue scan command with scan Id <scan_id> on subarray with the <subarray_id> using tmc
    Then the subarray obsState is transitioned to SCANNING
    And the MCCS subarray obsState is transitioned to READY after the scan duration elapsed
    And the TMC subarray obsState is transitioned back to READY
    Examples:
    | subarray_id   | scan_id  |
    |  1            |   1      |
