"""Country-default ancestry priors for site ancestry_mix inference.

Protocols rarely state population genetics; this deterministic layer fills
ancestry_mix from ISO country codes when Claude extraction omits it.
"""

from __future__ import annotations

from .models import Protocol, Site

# Pinned priors — documented assumptions, not gnomAD lookups.
_COUNTRY_DEFAULTS: dict[str, dict[str, float]] = {
    "IN": {"SAS": 1.0},
    "DE": {"EUR": 1.0},
    "US": {"EUR": 0.68, "AFR": 0.13, "AMR": 0.19},
    "GB": {"EUR": 1.0},
    "FR": {"EUR": 1.0},
}


def default_ancestry_mix(country: str) -> dict[str, float] | None:
    """Return pinned ancestry mix for a country code, or None if unknown."""
    return _COUNTRY_DEFAULTS.get(country.strip().upper())


def apply_ancestry_defaults(protocol: Protocol) -> Protocol:
    """Fill missing site ancestry_mix from country-code priors."""
    updated_sites: list[Site] = []
    changed = False
    for site in protocol.sites:
        if site.ancestry_mix:
            updated_sites.append(site)
            continue
        inferred = default_ancestry_mix(site.country)
        if inferred is None:
            updated_sites.append(site)
            continue
        updated_sites.append(site.model_copy(update={"ancestry_mix": inferred}))
        changed = True
    if not changed:
        return protocol
    return protocol.model_copy(update={"sites": updated_sites})
