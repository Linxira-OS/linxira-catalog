#!/usr/bin/env python3
"""Release reviewable items, permanently lock sensitive proxies.

Release to available:
- applications: heroic, bottles, flatseal (Flathub opt-in approved)
- components: python-pypi-tools, miniforge, samtools, bedtools, aligners,
  blast, fastqc, workflows (pip/conda official sources approved)

Permanently lock (review-channel, never auto-release):
- components: mihomo, clash-verge (proxy tools - sensitive, user must
  explicitly opt in via a separate process; keep locked)
"""
import json

CATALOG = "catalog/catalog-v3.json"
with open(CATALOG, encoding="utf-8") as f:
    data = json.load(f)

by_id = {it["id"]: it for it in data["applications"] + data["components"]}

RELEASE = [
    "heroic", "bottles", "flatseal",
    "component-python-pypi-tools", "component-miniforge",
    "component-samtools", "component-bedtools", "component-aligners",
    "component-blast", "component-fastqc", "component-workflows",
]
LOCK = ["component-mihomo", "component-clash-verge"]

for pid in RELEASE:
    item = by_id.get(pid)
    if not item:
        print(f"!! {pid} not found")
        continue
    item["review"] = {"status": "reviewed", "date": "2026-08-05",
                      "note": "Source reviewed; release approved."}
    item["availability"] = {"status": "available", "architectures": ["x86_64"],
                            "networkRequired": True, "offlinePolicy": "online-only",
                            "channel": "default"}
    print(f"released: {pid}")

for pid in LOCK:
    item = by_id.get(pid)
    if not item:
        print(f"!! {pid} not found")
        continue
    item["review"] = {"status": "reviewed", "date": "2026-08-05",
                      "note": "Proxy tool; permanently locked by project policy."}
    item["availability"] = {"status": "review-channel",
                            "architectures": ["x86_64"],
                            "channel": "optional-review",
                            "reason": "Proxy tool locked by policy; manual opt-in required.",
                            "offlinePolicy": "online-only"}
    print(f"permanently locked: {pid}")

with open(CATALOG, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
    f.write("\n")

# Final stats
apps = [it for it in data["applications"]]
comps = [it for it in data["components"]]
a_avail = sum(1 for it in apps if it.get("availability", {}).get("status") == "available")
a_lock = sum(1 for it in apps if it.get("availability", {}).get("status") == "review-channel")
c_avail = sum(1 for it in comps if it.get("availability", {}).get("status") == "available")
c_lock = sum(1 for it in comps if it.get("availability", {}).get("status") == "review-channel")
print(f"apps: {len(apps)} (available {a_avail}, locked {a_lock})")
print(f"components: {len(comps)} (available {c_avail}, locked {c_lock})")
