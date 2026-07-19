# Linxira Catalog

Canonical, versioned software component metadata for Linxira OS.

Catalog v2 is consumed by Calamares, Linxira Welcome, `linxira-config`, Shelly
recommendation links, and generated documentation. Package transactions remain
the responsibility of Calamares, Shelly, or an audited transaction backend.

The catalog now has two levels of selection:

- `applications[]` is the canonical list of individually selectable software
  items, grouped by category and source.
- `profiles[]` is a curated preset that will expand to application IDs. During
  the migration, legacy package arrays remain until Calamares and the installed
  Package Center consume application selections directly.

The same application IDs must be used by the installer, installed Package
Center, receipts and future CLI commands. A profile must never become the only
way to install software.

## Trust model

- Every source declares its package ecosystem and trust class.
- Miniforge channels are explicit sources: `conda-forge` and `bioconda` are
  verified third-party channels and are never enabled by the base system.
- Every application and profile declares architecture and network requirements.
- Every application and profile carries review status, review date, and
  presentation metadata.
- Catalog data contains package identifiers, never executable command strings.
- A profile ID is an allowlisted transaction request, not a shell fragment.

## Files

- `catalog/catalog-v2.json`: current reviewed catalog
- `schema/catalog-v2.schema.json`: JSON Schema Draft 2020-12 contract

Changes must pass schema validation plus semantic checks for unique IDs,
category references, source references, package names, and installer/catalog
chooser parity.
