import json
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "catalog-v3.json"
SCHEMA_PATH = ROOT / "schema" / "catalog-v3.schema.json"


class CatalogV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.sections = ("desktops", "applications", "components", "bundles", "operations")
        cls.nodes = {
            node["id"]: node
            for section in cls.sections
            for node in cls.catalog[section]
        }

    def test_schema_is_valid_and_catalog_conforms(self):
        self.assertEqual("catalog-v3.schema.json", self.catalog["$schema"])
        Draft202012Validator.check_schema(self.schema)
        validator = Draft202012Validator(
            self.schema, format_checker=FormatChecker()
        )
        errors = sorted(validator.iter_errors(self.catalog), key=lambda e: list(e.path))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_v2_compatibility_catalog_still_conforms(self):
        catalog = json.loads((ROOT / "catalog" / "catalog-v2.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schema" / "catalog-v2.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(catalog),
            key=lambda e: list(e.path),
        )
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_ids_are_unique_except_category_root_bundle_pairs(self):
        ids = [
            item["id"]
            for section in ("sources", "categories", *self.sections)
            for item in self.catalog[section]
        ]
        duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
        category_root_ids = sorted(
            item["id"]
            for item in self.catalog["categories"]
        )
        self.assertEqual(category_root_ids, duplicates)
        self.assertTrue(all(Counter(ids)[item] == 2 for item in duplicates))

    def test_all_references_resolve(self):
        node_ids = set(self.nodes)
        category_ids = {item["id"] for item in self.catalog["categories"]}
        source_ids = {item["id"] for item in self.catalog["sources"]}

        for category in self.catalog["categories"]:
            self.assertEqual([], sorted(set(category["children"]) - node_ids), category["id"])

        for section in ("desktops", "applications", "components"):
            for leaf in self.catalog[section]:
                self.assertIn(leaf["primaryCategory"], category_ids)
                self.assertIn(leaf["source"], source_ids)
                for field in ("requires", "recommends", "conflicts"):
                    unknown = sorted(set(leaf[field]) - node_ids)
                    self.assertEqual([], unknown, f"{leaf['id']}.{field}")

        for bundle in self.catalog["bundles"]:
            self.assertIn(bundle["primaryCategory"], category_ids)
            for role in ("required", "recommended", "optional"):
                unknown = sorted(set(bundle["children"][role]) - node_ids)
                self.assertEqual([], unknown, f"{bundle['id']}.{role}")

        for operation in self.catalog["operations"]:
            self.assertIn(operation["source"], source_ids)

    def test_primary_category_has_single_ownership(self):
        category_by_id = {item["id"]: item for item in self.catalog["categories"]}
        ownership = Counter(
            child
            for category in self.catalog["categories"]
            for child in category["children"]
        )
        categorized = self.catalog["desktops"] + self.catalog["applications"] + self.catalog["components"]

        for node in categorized:
            # 2026-08-13 交接文档 Bug #1: 预装项(timeshift/btop/firefox/okular/kate/fastfetch/
            # python/git/vpn-baseline)从分类 children 移除, 安装器视图模块只渲染分类内节点,
            # 实现"预装不进选择页"。条目保留(installerVisible:false)以维持依赖图与元数据完整。
            if not node.get("presentation", {}).get("installerVisible", True):
                self.assertEqual(0, ownership[node["id"]], node["id"])
                continue
            self.assertEqual(1, ownership[node["id"]], node["id"])
            self.assertIn(node["id"], category_by_id[node["primaryCategory"]]["children"])

        for application in self.catalog["applications"]:
            self.assertEqual(
                "applications", category_by_id[application["primaryCategory"]]["surface"]
            )
        for desktop in self.catalog["desktops"]:
            self.assertEqual(
                "desktops", category_by_id[desktop["primaryCategory"]]["surface"]
            )
        for node in self.catalog["components"]:
            self.assertEqual(
                "components", category_by_id[node["primaryCategory"]]["surface"]
            )
        for bundle in self.catalog["bundles"]:
            category = category_by_id[bundle["primaryCategory"]]
            self.assertEqual(bundle["surface"], category["surface"], bundle["id"])
            if bundle["id"] == bundle["primaryCategory"]:
                self.assertEqual(bundle["id"], bundle["primaryCategory"])
                self.assertEqual(0, ownership[bundle["id"]], bundle["id"])
            elif "workflow-only" not in bundle["tags"]:
                self.assertEqual(1, ownership[bundle["id"]], bundle["id"])
                self.assertIn(bundle["id"], category["children"])
            else:
                self.assertEqual(0, ownership[bundle["id"]], bundle["id"])

    def test_leaf_categories_have_matching_root_bundles(self):
        categories = {
            item["id"]: item
            for item in self.catalog["categories"]
            if item["surface"] in {"desktops", "applications"}
        }
        bundles = {
            item["id"]: item
            for item in self.catalog["bundles"]
            if item["surface"] in {"desktops", "applications"}
            and "category-root" in item["tags"]
        }
        self.assertEqual(set(categories), set(bundles))
        for category_id, category in categories.items():
            bundle = bundles[category_id]
            self.assertEqual([], bundle["children"]["required"], category_id)
            self.assertEqual([], bundle["children"]["recommended"], category_id)
            self.assertEqual(category["children"], bundle["children"]["optional"], category_id)

    def test_existing_domain_bundles_use_components_surface(self):
        domain_bundles = [
            item for item in self.catalog["bundles"]
            if item["id"].startswith("bundle-") and "workflow-only" not in item["tags"]
        ]
        self.assertTrue(domain_bundles)
        self.assertTrue(
            all(item["surface"] == "components" for item in domain_bundles)
        )

    def test_bundle_references_are_unique_and_graph_is_acyclic(self):
        bundles = {item["id"]: item for item in self.catalog["bundles"]}
        graph = {}
        for bundle_id, bundle in bundles.items():
            children = [
                child
                for role in ("required", "recommended", "optional")
                for child in bundle["children"][role]
            ]
            self.assertEqual(len(children), len(set(children)), bundle_id)
            self.assertNotIn(bundle_id, children)
            graph[bundle_id] = [child for child in children if child in bundles]

        visiting = set()
        visited = set()

        def visit(bundle_id):
            if bundle_id in visiting:
                self.fail(f"bundle cycle detected at {bundle_id}")
            if bundle_id in visited:
                return
            visiting.add(bundle_id)
            for child in graph[bundle_id]:
                visit(child)
            visiting.remove(bundle_id)
            visited.add(bundle_id)

        for bundle_id in graph:
            visit(bundle_id)

        self.assertTrue(any(graph.values()), "at least one nested bundle is required")

    def test_gaming_setup_is_a_hidden_fixed_workflow(self):
        bundles = {item["id"]: item for item in self.catalog["bundles"]}
        setup = bundles["bundle-gaming-setup"]
        self.assertIn("workflow-only", setup["tags"])
        self.assertIn("steam", setup["children"]["required"])
        self.assertIn("component-gaming-foundations", setup["children"]["required"])
        self.assertIn("component-open-gpu-runtime", setup["children"]["required"])
        components = {item["id"]: item for item in self.catalog["components"]}
        self.assertIn("umu-launcher", components["component-gaming-foundations"]["artifact"]["ids"])

    def test_proxy_review_candidates_are_never_default_available(self):
        components = {item["id"]: item for item in self.catalog["components"]}
        for component_id in ("component-mihomo", "component-clash-verge"):
            component = components[component_id]
            self.assertEqual("aur", component["provider"])
            # Locked by policy 2026-08-05: unavailable, never default.
            self.assertEqual("unavailable", component["availability"]["status"])
            self.assertFalse(component["presentation"]["defaultSelected"])

    def test_only_firefox_is_default_selected_browser_application(self):
        selected = [
            item["id"]
            for item in self.catalog["applications"]
            if item["presentation"]["defaultSelected"]
        ]
        # 2026-08-13 修订: timeshift/btop 移入离线基线必装(target-packages), 从 catalog 移除,
        # 安装器软件选择页不再显示(交接文档方案 A)。
        # 2026-08-13 追加: steam 默认勾选(游戏工具默认装载, 用户决策),
        # 组件侧 gaming-foundations/open-gpu-runtime 同步默认。
        self.assertEqual(["firefox", "steam"], sorted(selected))
        self.assertTrue(self.nodes["chromium"]["presentation"]["recommended"])
        self.assertFalse(self.nodes["chromium"]["presentation"]["defaultSelected"])
        self.assertEqual(
            ["desktop-plasma"],
            [item["id"] for item in self.catalog["desktops"] if item["presentation"]["defaultSelected"]],
        )
        # 2026-08-13 产品决策: 容器(Podman/Distrobox/Docker/Compose)与 Node.js 默认选中(桌面超算核心能力)
        # 2026-08-07 修订: Node.js 与 Apptainer 取消默认选中(与其他运行时一致; Apptainer 未审查)
        #   保留 Podman / Distrobox 默认选中(用户确认)
        # 2026-08-13 追加: docker/docker-compose 归入运行时(cap-containers)并默认选中(用户确认,
        #   容器运行时属系统能力, 与软件页划分: 运行时页默认勾选, 软件页用户可选)
        self.assertEqual(
            [
                "component-distrobox",
                "component-docker",
                "component-docker-compose",
                "component-gaming-foundations",
                "component-open-gpu-runtime",
                "component-podman",
            ],
            sorted(
                item["id"]
                for item in self.catalog["components"]
                if item["presentation"]["defaultSelected"]
            ),
        )
        # 2026-08-13 修订: 隐藏预设 cap-essential-online 已随方案 A 移除, 全部 bundle 不默认选中。
        self.assertFalse(
            any(
                item["presentation"]["defaultSelected"]
                for item in self.catalog["bundles"]
            )
        )

    def test_system_and_scientific_application_categories_are_broad_but_not_default(self):
        categories = {item["id"]: item for item in self.catalog["categories"]}
        self.assertEqual(
            ["octave", "paraview", "veusz", "labplot", "cantor", "rkward", "spyder", "sagemath"],
            categories["app-scientific"]["children"],
        )
        self.assertIn("partitionmanager", categories["app-system"]["children"])
        self.assertIn("gparted", categories["app-system"]["children"])
        self.assertIn("gnome-disk-utility", categories["app-system"]["children"])
        self.assertIn("filelight", categories["app-system"]["children"])
        self.assertIn("htop", categories["app-system"]["children"])
        self.assertIn("flatseal", categories["app-system"]["children"])

        for category_id in ("app-scientific", "app-system"):
            for child_id in categories[category_id]["children"]:
                child = self.nodes[child_id]
                self.assertFalse(child["presentation"]["defaultSelected"], child_id)
                if child_id != "flatseal":
                    self.assertEqual("arch", child["source"], child_id)
                    self.assertEqual("pacman", child["provider"], child_id)

        self.assertEqual("flathub", self.nodes["flatseal"]["source"])
        # flatseal released 2026-08-05 (Flathub opt-in approved); channel is default now.
        self.assertEqual("default", self.nodes["flatseal"]["availability"]["channel"])

    def test_selection_policies_are_complete_and_safe(self):
        selectable = self.catalog["categories"] + self.catalog["desktops"] + self.catalog["applications"] + self.catalog["components"] + self.catalog["bundles"]
        modes = {item["selection"]["mode"] for item in selectable}
        self.assertEqual({"multi", "exclusive", "preset"}, modes)

        defaults = {
            item["id"]: item["presentation"]["defaultSelected"]
            for item in self.catalog["desktops"] + self.catalog["applications"] + self.catalog["components"] + self.catalog["bundles"]
        }
        for category in self.catalog["categories"]:
            mode = category["selection"]["mode"]
            selected_count = sum(defaults[child] for child in category["children"])
            if mode == "exclusive":
                self.assertLessEqual(selected_count, 1, category["id"])
            elif mode == "bounded":
                self.assertLessEqual(selected_count, category["selection"]["maxSelected"], category["id"])
                self.assertLess(category["selection"]["maxSelected"], len(category["children"]), category["id"])
            self.assertNotEqual("preset", mode, "categories are organization nodes, not presets")

        for category in self.catalog["categories"]:
            if category["surface"] == "applications":
                self.assertEqual("multi", category["selection"]["mode"], category["id"])

        for bundle in self.catalog["bundles"]:
            self.assertEqual("preset", bundle["selection"]["mode"], bundle["id"])

    def test_provider_source_boundaries(self):
        source_kinds = {item["id"]: item["kind"] for item in self.catalog["sources"]}
        for leaf in self.catalog["desktops"] + self.catalog["applications"] + self.catalog["components"]:
            self.assertEqual(leaf["provider"], source_kinds[leaf["source"]], leaf["id"])
        for operation in self.catalog["operations"]:
            self.assertEqual("builtin", source_kinds[operation["source"]])

    def test_review_channel_and_wps_policy(self):
        sources = {item["id"]: item for item in self.catalog["sources"]}
        for leaf in self.catalog["desktops"] + self.catalog["applications"] + self.catalog["components"]:
            if leaf["availability"]["channel"] == "optional-review":
                self.assertTrue(
                    sources[leaf["source"]]["userOptInRequired"]
                    or leaf["license"]["requiresAcceptance"],
                    leaf["id"],
                )
                self.assertNotEqual("reviewed", leaf["review"]["status"], leaf["id"])
                self.assertFalse(leaf["presentation"]["defaultSelected"], leaf["id"])

        wps = self.nodes["wps-office"]
        self.assertEqual("aur", wps["source"])
        self.assertEqual("aur", wps["provider"])
        self.assertEqual("proprietary", wps["license"]["classification"])
        self.assertEqual("legal-review-pending", wps["review"]["status"])
        self.assertEqual("optional-review", wps["availability"]["channel"])
        self.assertFalse(wps["presentation"]["defaultSelected"])

    def test_printing_and_scanning_is_optional_critical_capability(self):
        bundle = self.nodes["bundle-printing-scanning"]
        self.assertTrue(bundle["criticalSystemCapability"])
        self.assertFalse(bundle["presentation"]["defaultSelected"])
        members = {
            child
            for role in ("required", "recommended", "optional")
            for child in bundle["children"][role]
        }
        self.assertTrue(
            {
                "component-cups",
                "component-printer-config",
                "component-sane",
                "component-network-discovery",
                "operation-test-print-scan-network",
            }.issubset(members)
        )
        for component_id in (
            "component-cups",
            "component-printer-config",
            "component-sane",
            "component-network-discovery",
        ):
            self.assertTrue(self.nodes[component_id]["criticalSystemCapability"])

    def test_required_domain_bundles_exist(self):
        required = {
            "bundle-runtime-management",
            "bundle-developer-workstation",
            "bundle-data-science",
            "bundle-bioinformatics",
            "bundle-scientific-computing",
            "bundle-gis",
            "bundle-research-writing",
            "bundle-container-workstation",
        }
        self.assertTrue(required.issubset(self.nodes))

    def test_desktop_category_is_exclusive_with_exact_reviewed_cohorts(self):
        category = next(item for item in self.catalog["categories"] if item["id"] == "desktop-environments")
        self.assertEqual(category["surface"], "desktops")
        self.assertEqual(category["selection"], {"mode": "exclusive"})
        # 2026-08-09 产品决策: 多桌面支持(对标 CachyOS 17+ 桌面), 全部 reviewed 可选
        # 2026-08-12 产品决策: 新增 Cinnamon(最接近 Windows 体验, 资源占用更低)
        # 2026-08-13 产品决策: 新增 LXQt/LXDE/MATE/Budgie/i3/Openbox; 全部联网安装
        self.assertEqual(
            category["children"],
            ["desktop-plasma", "desktop-gnome", "desktop-xfce",
             "desktop-hyprland", "desktop-sway", "desktop-cosmic",
             "desktop-cinnamon", "desktop-lxqt", "desktop-lxde",
             "desktop-mate", "desktop-budgie", "desktop-i3",
             "desktop-openbox"],
        )
        self.assertEqual(
            [d["id"] for d in self.catalog["desktops"]
             if d["review"]["status"] == "reviewed"],
            ["desktop-plasma", "desktop-gnome", "desktop-xfce",
             "desktop-hyprland", "desktop-sway", "desktop-cosmic",
             "desktop-cinnamon", "desktop-lxqt", "desktop-lxde",
             "desktop-mate", "desktop-budgie", "desktop-i3",
             "desktop-openbox"],
        )

        xfce = self.nodes["desktop-xfce"]
        self.assertEqual(xfce["availability"]["offlinePolicy"], "online-only")
        lxqt = self.nodes["desktop-lxqt"]
        self.assertEqual(lxqt["review"]["status"], "reviewed")
        self.assertEqual(lxqt["availability"]["offlinePolicy"], "online-only")
        self.assertIn("desktop-plasma", lxqt["conflicts"])
        self.assertNotIn("desktop-lxqt", lxqt["conflicts"])

        gnome = self.nodes["desktop-gnome"]
        self.assertEqual(
            gnome["artifact"]["ids"],
            [
                "file-roller", "gnome-control-center", "gnome-disk-utility",
                "gnome-keyring", "gnome-session", "gnome-shell",
                "gnome-text-editor", "gnome-tweaks", "gdm", "ptyxis",
            ],
        )
        plasma = self.nodes["desktop-plasma"]
        self.assertEqual(plasma["review"]["status"], "reviewed")
        self.assertEqual(plasma["availability"]["offlinePolicy"], "included")
        self.assertEqual(gnome["review"]["status"], "reviewed")
        self.assertEqual(gnome["availability"]["status"], "available")
        self.assertEqual(gnome["availability"]["channel"], "default")
        self.assertEqual(gnome["availability"]["offlinePolicy"], "online-only")

        root = self.nodes["desktop-environments"]
        self.assertEqual(root["surface"], "desktops")
        self.assertEqual(root["children"]["optional"], category["children"])


if __name__ == "__main__":
    unittest.main()
