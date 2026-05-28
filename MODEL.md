# Corporate Carbon Ledger Architecture: Data Model Specifications

This document defines the production data schema implemented for the BreatheESG ledger engine. The design prioritizes immutable data lineage, multi-tenant workspace isolation, and high-performance querying for third-party compliance audits.

## Entity Relationship Overview
The schema intentionally decouples raw data ingestion lineage from normalized accounting lines. This ensures a one-to-many relationship where a single messy multi-source data file can explode into multiple explicit ledger records, preserving full visibility for compliance tracing.

### 1. Organization Model (Multi-Tenant Routing Core)
Acts as the global data isolation boundary. Cross-tenant queries are structurally prevented at the database layer.
* `id` (UUID, Primary Key): Explicit UUID protection preventing resource enumeration attacks.
* `name` (VarChar, Unique, Indexed): Matches corporate tenant workspace profiles (e.g., `Acme_Corp_HQ`).

### 2. IngestionJobLog (Data Lineage Tracker)
The immutable master track record for data origin tracing.
* `id` (UUID, Primary Key)
* `organization` (ForeignKey -> Organization, ON DELETE CASCADE)
* `source_type` (VarChar, Choices: `SAP`, `UTILITY`, `TRAVEL`): Identifies the parsing engine routing channel.
* `filename` (VarChar, Nullable): Tracks the original naming artifact for file-based streams.
* `raw_payload_backup` (TextField): Stores the unmodified raw string payload (unparsed CSV chunks or API JSON structures). Never altered, giving auditors an absolute historical baseline.

### 3. EmissionActivityRecord (The Single Source of Truth Ledger)
The transactional engine of the application. Designed as an append-only historical log.
* `id` (UUID, Primary Key)
* `organization` (ForeignKey -> Organization, Indexed)
* `job_source` (ForeignKey -> IngestionJobLog, ON DELETE PROTECT): Protected constraint preventing deletion of parent logs if active ledger lines point to them.
* `scope_category` (VarChar, Choices: `SCOPE_1`, `SCOPE_2`, `SCOPE_3`, Indexed)
* `ghg_mapping_category` (VarChar): Maps raw inputs to standard greenhouse gas accounting labels.
* `original_quantity` & `original_unit`: Preserves the raw data metric exactly as received from the source.
* `normalized_quantity_co2e` (Decimal, 15, 4): Calculated greenhouse mass equivalent in Metric Tons (MT).
* `activity_start_date` & `activity_end_date` (Date, Indexed): Supports exact arbitrary time boundary filtering and proration handling.
* `validation_status` (VarChar, Choices: `PENDING`, `VALID`, `SUSPICIOUS`, `FAILED`, Indexed): Captures programmatic anomaly detection engine outputs.
* `approval_status` (VarChar, Choices: `DRAFT`, `APPROVED`, `REJECTED`, Indexed): Captures human-in-the-loop review actions.
* `is_locked` (Boolean, Default=False, Indexed): The state-machine terminal flag. When True, all database modifications to this row trigger a validation error.
* `approved_by` (ForeignKey -> User, SET_NULL) & `approved_at` (DateTimeField): Cryptographic/Audit handshakes recording the human review trace.

## Data Model Defense
1. **Decimal vs. Float**: All metric volumes and calculations utilize Django `DecimalField` (SQL `numeric`). Floats introduce binary rounding approximations which are unacceptable for statutory financial or environmental compliance audits.
2. **State-Machine Immutability Lock**: The `clean()` method utilizes `self._state.adding` to completely isolate creation and modification contexts. Once a record's `is_locked` flag shifts to `True`, the database layer rejects all updates.
3. **Race Condition Prevention**: The ledger's sign-off pipeline utilizes database row-level locking via `select_for_update()`. This forces concurrent analyst sessions to execute sequentially, preventing dual-approval race conditions.