from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from sitepulse.scanner import normalize_url


def _is_public_ip(address: str) -> bool:
    try:
        return ipaddress.ip_address(address).is_global
    except ValueError:
        return False


def validate_public_url(url: str) -> str:
    """Validate that an API scan target resolves only to public IP addresses.

    This prevents callers from using the scanner to access localhost,
    private networks, link-local services, or other non-public targets.
    """
    normalized = normalize_url(url)
    parsed = urlparse(normalized)
    hostname = parsed.hostname

    if not hostname:
        raise ValueError("URL must contain a hostname.")

    lowered = hostname.lower().rstrip(".")
    if lowered == "localhost" or lowered.endswith(".localhost"):
        raise ValueError("Only public website URLs can be scanned.")

    try:
        literal_ip = ipaddress.ip_address(lowered)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if not literal_ip.is_global:
            raise ValueError("Only public website URLs can be scanned.")
        return normalized

    try:
        address_info = socket.getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise ValueError("The website hostname could not be resolved.") from exc

    addresses = {item[4][0] for item in address_info}

    if not addresses or any(not _is_public_ip(address) for address in addresses):
        raise ValueError("Only public website URLs can be scanned.")

    return normalized
