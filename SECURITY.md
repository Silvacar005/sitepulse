# Security

## Supported version

Security improvements are applied to the latest version of SitePulse.

## Scan-target restrictions

SitePulse is designed to scan public HTTP and HTTPS websites. API requests are
validated before crawling to reject obvious non-public targets, including:

- localhost
- loopback addresses
- private address ranges
- link-local addresses
- hostnames that resolve to non-public IP addresses

This reduces the risk of the scanner being used for server-side request forgery
against internal services.

## Limitations

DNS can change after validation, and network security is a defense-in-depth
problem. A production deployment should additionally use infrastructure-level
egress controls if stronger SSRF guarantees are required.

SitePulse also caps API crawl and link-check sizes to reduce accidental resource
exhaustion.

## Reporting

If you discover a security issue in this portfolio project, please report it
privately to the repository owner rather than publishing exploit details in a
public issue.
