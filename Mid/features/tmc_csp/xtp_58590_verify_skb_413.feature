Feature: SKB-413

	
	@XTP-28347 @XTP-29583 @XTP-58590 @Team_SAHYADRI
	Scenario: Verify SKB-413 with TMC as entrypoint
		Given the telescope is in ON state
		And TMC SubarrayNode is in ObsState IDLE with assigned receptors <receptors>
		When I issue the Configure command to the TMC SubarrayNode
		Then CspSubarrayLeafNode delay model points to correct assigned receptors <receptors>
		And the TMC subarray transitions to ObsState READY
		Examples:
		    | receptors            |
		    | ['SKA063', 'SKA100'] |