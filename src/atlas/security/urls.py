"""SSRF-aware URL restrictions for fetch tools."""

from __future__ import annotations

from ipaddress import ip_address, ip_network
from urllib.parse import urlparse

from atlas.config.settings import Settings


class UrlBlockedError(ValueError):
    """Raised when a URL is not allowed for outbound fetch."""


_PRIVATE_NETWORKS = [
    ip_network("10.0.0.0/8"),
    ip_network("127.0.0.0/8"),
    ip_network("169.254.0.0/16"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("::1/128"),
]


def assert_public_url(url: str, settings: Settings) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in settings.allowed_schemes:
        raise UrlBlockedError(f"scheme not allowed: {parsed.scheme}")
    host = (parsed.hostname or "").lower()
    if not host:
        raise UrlBlockedError("missing host")
    if host in {h.lower() for h in settings.blocked_host_list if "/" not in h}:
        raise UrlBlockedError(f"blocked host: {host}")
    try:
        addr = ip_address(host)
    except ValueError:
        return
    if any(addr in net for net in _PRIVATE_NETWORKS):
        raise UrlBlockedError("private or link-local address blocked")
