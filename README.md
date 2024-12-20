# SKA Telescope Integration Testing

This repository provides a comprehensive guide for running integration tests on the SKA Telescope's Low and Mid systems. The tests ensure that the telescope components work seamlessly in their deployment environments. Below is an overview of the testing process, organized into Low and Mid telescopes, with details on system-level and pairwise testing.

---

## Overview
The testing framework consists of two phases:

1. **Pairwise Testing:** Tests interactions between specific subsystems.
2. **System-Level Testing:** Verifies the functionality of the entire system.

### Key Commands
- **Run all tests:**
  ```bash
  make k8s-test
  ```
- **Run specific tests:**
  ```bash
  make k8s-test MARK=<test_marker>
  ```
  Replace `<test_marker>` with the appropriate marker for your test type (e.g., `tmc_sdp`, `system_level_tests`, etc.).

---

## Testing for Low Telescope
The Low telescope tests are divided into:

### 1. Pairwise Testing
This phase tests interactions between subsystems:

- **TMC and CSP:**
  ```bash
  make k8s-test MARK=tmc_csp
  ```
- **TMC and SDP:**
  ```bash
  make k8s-test MARK=tmc_sdp
  ```
- **TMC and MCCS:**
  ```bash
  make k8s-test MARK=tmc_mccs
  ```

### 2. System-Level Testing
This phase ensures the entire Low telescope system operates correctly:

- **Run system-level tests:**
  ```bash
  make k8s-test MARK=system_level_tests
  ```

---

## Testing for Mid Telescope
The Mid telescope tests are also divided into:

### 1. Pairwise Testing
This phase tests interactions between subsystems:

- **TMC and CSP:**
  ```bash
  make k8s-test MARK=tmc_csp
  ```
- **TMC and SDP:**
  ```bash
  make k8s-test MARK=tmc_sdp
  ```
- **TMC and Dish:**
  ```bash
  make k8s-test MARK=tmc_dish
  ```

### 2. System-Level Testing
This phase ensures the entire Mid telescope system operates correctly:

- **Run system-level tests:**
  ```bash
  make k8s-test MARK=system_level_tests
  ```

---

## Flowcharts

### Telescope Testing Workflow
```text
                    +---------------------+
                    |     Telescope      |
                    +---------------------+
                              |
                 +------------+-----------+
                 |                        |
         +-------+-------+        +-------+-------+
         |      Low       |        |      Mid       |
         +---------------+        +---------------+
                 |                        |
    +-----------+-----------+   +-----------+-----------+
    |                       |   |                       |
+---+---+             +-----+-----+             +-------+---+
| Pairwise|            | System Level|            | Pairwise  |
| Testing |            |   Testing   |            | Testing   |
+---------+            +-------------+            +-----------+
```

### Pairwise Testing for Low and Mid Telescopes
```text
+-----------------+          +-----------------+
|     Low         |          |     Mid         |
+-----------------+          +-----------------+
| TMC_CSP         |          | TMC_CSP         |
| TMC_SDP         |          | TMC_SDP         |
| TMC_MCCS        |          | TMC_DISH        |
+-----------------+          +-----------------+
```

### System-Level Testing Workflow
```text
+---------------------+
| System Level Tests |
+---------------------+
       |
+---------------------+
| Verifies Full System|
+---------------------+
```

---

## Repository Links
- **Low Integration Tests:** [SKA Low Integration](https://gitlab.com/ska-telescope/ska-low-integration)
- **Mid Integration Tests:** [SKA Mid Integration](https://gitlab.com/ska-telescope/ska-mid-integration)

---

## Notes
- Ensure the environment is properly set up before running any tests.
- Use the `MARK` parameter to specify the type of test to run.
- Refer to the respective repositories for additional details.

