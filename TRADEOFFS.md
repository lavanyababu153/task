# Strategic Project Engineering Tradeoffs

To ensure a robust, reliable compliance core within a tight 4-day sprint, the following three system capabilities were intentionally omitted from the prototype.

## 1. Asynchronous Task Queuing Architecture (Celery + Redis)
* **What it does**: Offloads large data file parsing operations out of the web request/response cycle into background worker threads.
* **Why it was omitted**: Implementing Celery adds extra infrastructure overhead (Redis/RabbitMQ message brokers) that can complicate early deployment environments. For our prototype scope, processing files inline inside standard Django database transactions keeps things completely predictable.
* **Production Mitigation Path**: As file rows scale past 50,000 items per upload, we will wrap the base engine execution inside a standard Celery task structure to prevent web server request timeouts.

## 2. Dynamic Emissions Factor API Integrations (Climatiq / Open Emissions Index)
* **What it does**: Queries live third-party databases to fetch region-specific, real-time grid mix emissions intensity variables.
* **Why it was omitted**: External API webhooks introduce single-point-of-failure liabilities during data ingestion pipelines. For this prototype, we utilize localized static compliance constants (e.g., `0.00039 MT CO2e/kWh` for standard regional electricity).
* **Production Mitigation Path**: Implement a cached data table storing standard regulatory carbon metrics (EPA eGRID, DEFRA) updated once per year, eliminating live network dependency constraints.

## 3. Inline User Editing of Stored Database Records
* **What it does**: Provides spreadsheet-like fields directly on the React frontend dashboard table for manual cell updates.
* **Why it was omitted**: Direct database mutation fields bypass data lineage and compromise audit transparency.
* **Production Mitigation Path**: The application enforces an append-only architecture. If an input error occurs, users execute a reversal entry transaction rather than manually altering an existing row, preserving an absolute audit trail for compliance verification.