@SP-4029
Feature: TMC Dish Pointing (ADR-95 and ADR-76)
	#Most of the ADR-95 related functionality agreed to be implemented in PI21, was implemented in PI21. The only remaining change is to pass the ScanID via the Scan command. See ADR-95 page in Confluence: 
	#[https://confluence.skatelescope.org/display/SWSI/ADR-95+DISH+Pointing]
	@XTP-49147 @XTP-28347
	Scenario: TMC is able to process pointing calibration received from SDP during five point calibration scan.
		Given a TMC
		When I assign resources for five point calibration scan
		And I configure subarray for a calibration scan
		And I invoke calibration scan five times with scan ids <scan_ids>
		Then the TMC receive pointing calibration from SDP and applies them to the Dishes

		Examples:
			| scan_ids                                                            |
			| 1,2,3,4,5                                                           |