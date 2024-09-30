Feature: TMC performs ReleaseResources on MCCS subsystem

	@XTP-30608 @XTP-30488 @Team_HIMALAYA
	Scenario: Release resources from MCCS Subarray using TMC
		Given the Telescope is in ON state
		And TMC subarray <subarray_id> in the IDLE obsState
		When I release the assigned resources for subarray using TMC
		Then the MCCS subarray must be in EMPTY obsState
		And TMC subarray obsState transitions to EMPTY
		Examples:
		| subarray_id   |
		|  1            |