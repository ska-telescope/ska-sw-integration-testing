Feature:This feature describes assigning, releasing, and configuring resources for the Low telescope subarray 
    with TMC, including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

@XTP-65635 @XTP-64112 @TEAM_HIMALAYA
Scenario: Assign resources to Low subarray
    Given a Low telescope
    And telescope is in ON state
    And subarray is in EMPTY ObsState
    When I assign resources to the subarray
    Then the TMC, CSP, SDP, and MCCS subarrays transition to RESOURCING obsState
    And the TMC, CSP, SDP, and MCCS subarrays transition to IDLE obsState

@XTP-65636 @XTP-64112 @TEAM_HIMALAYA
Scenario: Release resources from Low subarray
    Given a Low telescope
    And telescope is in ON state
    And subarray is in the IDLE obsState
    When I release all resources assigned to it
    Then the TMC, CSP, SDP and MCCS subarray must be in EMPTY obsState


@XTP-66007 @XTP-64112
Scenario: Configure the Low telescope subarray using TMC
	Given a Low telescope
	And telescope is in ON state
	And subarray is in IDLE ObsState
	When I configure it for a scan
	Then the TMC, CSP, SDP, and MCCS subarrays transition to CONFIGURING obsState
	And the TMC, CSP, SDP, and MCCS subarrays transition to READY obsState
  

@XTP-66037 @XTP-64112
Scenario: End Configuration to the low telescope subarray using TMC
	Given a Low telescope
	And telescope is in ON state
	And subarray is in READY ObsState
	When I end the configuration
	Then the TMC, CSP, SDP and MCCS subarrays transition to IDLE obsState

Scenario: Execute Scan on the Low telescope
    Given a Low telescope
    And telescope is in ON state
    And subarray is in READY ObsState with <scan_duration> scan_duration
    When I invoke scan command with scan id <scan_id>
    Then the TMC, CSP, SDP and MCCS subarrays transition to SCANNING obsState
    And after the scan duration it transition back to READY obsState
    Examples:
        |scan_duration     |scan_id   |
        |10.0              |1         |
        |15.0              |2         |

Scenario: EndScan to the low telescope subarray using TMC
	Given a Low telescope
	And telescope is in ON state
	And subarray is in SCANNING obsState
	When I end the scan
	Then the TMC, CSP, SDP and MCCS subarrays transition to READY obsState