# Security and Operations Plan

## Product requirement: preserve scraper functionality

This project is intended to remain a full-featured scraping and research toolkit. This plan does not call for deleting modules, reducing extraction coverage, removing supported data sources, or arbitrarily lowering crawl depth, concurrency, or output detail.

The objective is to protect the service boundary and the operator's infrastructure while preserving legitimate scraping and research workflows.

## Current API exposure

The current API server exposes module execution and bulk-scan routes without visible authentication. It also starts an interactive CLI subprocess for each request. A network-reachable unauthenticated execution interface creates an unacceptable risk of unauthorized use, resource exhaustion, data exposure, and unintended activity against third-party systems.

## Required implementation sequence

1. **Authentication at the API boundary**
   - Require an operator-managed credential for every non-health API route.
   - Load credentials only from environment variables or a secret manager; never commit them.
   - Compare credentials safely and return a generic unauthorized response.
   - Keep local CLI use available independently of API authentication.

2. **Transport and deployment**
   - Bind the application to loopback by default for local use.
   - For remote deployment, terminate TLS at a trusted reverse proxy and do not expose the raw application port publicly.
   - Document secure secret provisioning and rotation.

3. **Execution reliability**
   - Replace fragile interactive subprocess assumptions with explicit, structured task interfaces in a separately reviewed change.
   - Apply request timeouts, bounded worker capacity, cancellation, and cleanup of child processes.
   - Return task IDs and structured status for long-running jobs rather than holding unbounded requests open.
   - Redact secrets and sensitive response data from logs.

4. **Scraping quality and operator controls**
   - Preserve supported extraction and crawl features.
   - Make crawl depth, concurrency, retries, timeouts, user-agent, output formats, and source selection explicit configuration rather than silently reducing them.
   - Respect applicable site terms, access permissions, robots directives where applicable, and privacy requirements.
   - Provide per-job limits and clear operator-configurable resource budgets to protect the host; document defaults and how an authorized operator changes them.

5. **Testing**
   - Add tests for authentication, unauthorized requests, malformed inputs, timeout/cancellation, subprocess cleanup, and ordinary scraping behavior.
   - Add regression tests demonstrating that supported scraping workflows still work after API hardening.
   - Add CI for syntax checks and the test suite once the repository's test layout and dependency setup are verified.

## Scope boundary

This plan preserves legitimate web scraping, crawling, image/data extraction, reporting, and research capabilities. It does not authorize making credential attacks, denial-of-service, destructive payloads, persistence, or remote-shell operations easier to launch against systems. Those high-risk operations require separate safety review and are not part of the scraping API's supported remote execution surface.

## Acceptance criteria

- Existing legitimate scraping workflows remain available.
- No non-health API endpoint is callable without authentication.
- Remote deployment uses TLS and secret-managed credentials.
- Jobs have bounded resource use, timeouts, cancellation, and cleanup.
- Tests verify both security controls and scraping-feature regression coverage.
- No secrets are committed, printed, or returned in API responses.
