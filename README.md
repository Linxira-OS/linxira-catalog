# Linxira Catalog

Canonical, versioned software component metadata for Linxira OS.

Catalog v3 is the canonical graph for new installer, Package Center and
Bundle/Component Manager work. Catalog v2 remains unchanged as a compatibility
input for existing consumers. Package transactions remain the responsibility
of an audited planning and transaction backend.

Catalog v3 separates three product surfaces while sharing stable IDs and one
selection model:

- `desktops[]` contains reviewed, mutually exclusive desktop cohorts.
- `applications[]` contains individually selectable ordinary software.
- `components[]` contains runtimes, tools and system capabilities.
- `bundles[]` are expandable presets with an explicit `desktops`, `applications`
  or `components` surface and `required`, `recommended` and `optional` references.
  Bundles may nest other bundles and must form a DAG.
- Every desktop or applications category has a same-ID category-root bundle whose members
  exactly mirror the category children, in order, as optional references.
- `operations[]` contains fixed, controlled action IDs. Catalog data never
  contains executable shell strings.
- `categories[]` owns each desktop, application, component or bundle through exactly one
  `primaryCategory`; application categories are multi-select, while desktop
  environment categories may be mutually exclusive.
- Bundles declare `preset`; selecting one changes leaf defaults but does not
  create an opaque installation artifact.

The same stable IDs must be used by the installer, installed managers, plans,
receipts and CLI handoffs. Selection and receipts are keyed by leaf ID, not by a
tree path. Catalog v2 `profiles[]` remain only for compatibility and must not be
used as the v3 capability model.

## Trust model

- Every source declares its package ecosystem and trust class.
- Miniforge channels are explicit sources: `conda-forge` and `bioconda` are
  verified third-party channels and are never enabled by the base system.
- Every leaf declares provider, artifact, scope, source, license, review,
  availability, offline policy, size and dependency metadata.
- External ecosystems are disabled by default and require explicit user opt-in.
- Pending proprietary or third-party candidates remain in the optional review
  channel and are never default-selected.
- Catalog data contains package identifiers, never executable command strings.
- A profile ID is an allowlisted transaction request, not a shell fragment.

## Files

- `catalog/catalog-v2.json`: current reviewed catalog
- `schema/catalog-v2.schema.json`: JSON Schema Draft 2020-12 contract
- `catalog/catalog-v3.json`: application/component/bundle graph
- `schema/catalog-v3.schema.json`: strict v3 JSON Schema Draft 2020-12 contract
- `tests/test_catalog_v3.py`: schema and semantic validation

Install development requirements and run:

```sh
python -m unittest discover -s tests -v
```

Validation covers the schema, category-root ID pairs and all other global IDs,
references, primary-category ownership, bundle surfaces, nested bundle
acyclicity, duplicate members, provider/source boundaries, reviewed browser
application defaults, review-channel policy, printing/scanning
capability coverage and the selection modes used by the catalog.
