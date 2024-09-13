@XTP-28568
Scenario: Successful Execution of Scan Command on Low Telescope Subarray in TMC
    Given a TMC
    Given a subarray in READY obsState
    When I command it to scan for a given period
    Then the subarray must be in the SCANNING obsState until finished
