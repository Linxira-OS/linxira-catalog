# Linxira Catalog

Canonical, versioned software component metadata for Linxira OS.

Catalog v2 is consumed by Calamares, Linxira Welcome, `linxira-config`, Shelly
recommendation links, and generated documentation. Package transactions remain
the responsibility of Calamares, Shelly, or an audited transaction backend.

## Trust model

- Every source declares its package ecosystem and trust class.
- Every profile declares architecture and network requirements.
- Every profile carries review status, review date, and presentation metadata.
- Catalog data contains package identifiers, never executable command strings.
- A profile ID is an allowlisted transaction request, not a shell fragment.

## Files

- `catalog/catalog-v2.json`: current reviewed catalog
- `schema/catalog-v2.schema.json`: JSON Schema Draft 2020-12 contract

Changes must pass schema validation plus semantic checks for unique IDs,
category references, source references, package names, and installer/catalog
chooser parity.
