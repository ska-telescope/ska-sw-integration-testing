Feature: TMC performs AssignResources on MCCS subsystem
	
	@XTP-30490 @XTP-30488 @Team_HIMALAYA
	Scenario: Assigning Resources to MCCS Subarray
		Given the Telescope is in the ON state
		And the obsState of subarray is EMPTY
		When I assign resources with the <subarray_id> to the subarray using TMC
		Then the MCCS subarray obsState must transition to IDLE
		And the TMC subarray obsState is transitioned to IDLE
		And the correct resources <station_ids> are assigned to the MCCS subarray
		Examples:
		| subarray_id | station_ids       |
		| 1           | "ci-1", "ci-2"    |