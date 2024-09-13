@XTP-60175 @XTP-29682 @tmc_csp
Scenario: verify SKB-476
    Given the Telescope is in ON state
    And subarray node is in observation state IDLE
    When I invoke configure command without <key> in csp configure json
    Then csp subbaray node transitions to observation state READY
    And subarray node transitions to observation state READY
    Examples:
    | key         |
    | timing_beams|