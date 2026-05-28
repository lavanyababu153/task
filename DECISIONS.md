# Architectural Decisions & Ambiguity Resolutions

This document captures the real-world constraints, compromises, and design paths chosen to build the BreatheESG ledger engine.

## Ambiguity Resolutions & Assumptions

### 1. SAP Stream Scope Boundary
* **Ambiguity**: SAP data structures can be queried via IDocs, OData REST API layers, or direct flat ALV Grid reports.
* **Resolution**: Handled data assuming a standard SAP ALV Grid text export pattern. We isolate technical German header layouts (`MENG` for Quantity, `MEINS` for Unit, `WERKS` for Plant, `BUDAT` for Posting Date).
* **Justification**: In early-stage enterprise onboarding, direct system-to-system API integration typically takes months due to firewall security clearances. Supporting flat-file ALV Grid raw text extractions allows companies to achieve immediate data ingestion on day one.

### 2. Non-Calendar Utility Billing Cycles
* **Ambiguity**: Facilities teams pull bills that cross calendar month boundaries (e.g., April 12th to May 14th).
* **Resolution**: The schema tracks explicit `activity_start_date` and `activity_end_date` date ranges instead of assigning items to an arbitrary single month string.
* **Justification**: This supports precise time-series database interpolation, allowing downstream analytics engines to prorate carbon footprints down to the exact day for standardized monthly reporting.

### 3. Corporate Travel Distance Data
* **Ambiguity**: Corporate travel payloads from platforms like Concur frequently omit calculated distances, providing only origin and destination IATA airport codes.
* **Resolution**: Built an internal lookup map containing global IATA hub coordinates, passing them through a backend mathematical Haversine formula module to compute true flight leg kilometers dynamically.

## What I Would Clarify With The PM
1. **Rejection Workflows**: When an analyst marks a ledger line item as `REJECTED`, should the system allow them to manually input a re-calculation correction override, or must the source system generate a corrected file import job?
2. **Multi-Tenant Permissions**: Do analysts have global access across all client enterprises, or do we need strict role-based access control (RBAC) scopes mapped directly to individual organizations?