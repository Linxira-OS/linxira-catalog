#!/usr/bin/env python3
"""把 OpenOffice / LibreOffice / ONLYOFFICE 三件办公套件补齐为推荐项(catalog-v3.json)。

用户口径(2026-10-14):「OpenOffice、LibreOffice 和 OnlyOffice 这个加上」。

事实基础(2026-10-14 实核: AUR RPC + AUR PKGBUILD 直读):
- **OpenOffice**: AUR 里的包名是 `openoffice-bin`(4.1.16-1, 47 票, 2026-05 更新);
  `apache-openoffice` / `apache-openoffice-bin` **在 AUR 不存在**(RPC 返回空)
  —— 勿按上游项目名猜包名。该包 license=Apache, 是上游官方 RPM 二进制重打包,
  装到 `/opt/openoffice4`, 与 LibreOffice(/usr/lib/libreoffice)并存不冲突。
- **LibreOffice**: 本仓早有 `libreoffice`(pacman/arch = libreoffice-fresh ⇒ installer-eligible);
  上一轮按用户口径降为不推荐, 本轮按新口径把推荐标打开; `libreoffice-still` 保持非推荐(只作替代项)。
- **ONLYOFFICE**: 本仓早有 `onlyoffice`(aur/onlyoffice-bin)且 recommended 本来就是 true;
  本轮把它从 `bundle-office-suite` 的 optional 提到 recommended。

写回格式与原文一致: json.dumps(indent=2, ensure_ascii=False) + CRLF + 尾换行。
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "catalog" / "catalog-v3.json"
DATE = "2026-10-14"
# 实测值(2026-10-14): 上游 Apache_OpenOffice_4.1.16_Linux_x86-64_install-rpm_en-US.tar.gz
# 内 44 个 RPM 的载荷解包体积之和 = 406,717,148 B = 387.9 MiB(≈388 MiB)。
# 口径同其它条目(Installed-Size), 非下载体积(上游 .tar.gz 仅 158.6 MiB)。
OPENOFFICE_SIZE_MIB = 388
OPENOFFICE_NOTE = (
    "AUR openoffice-bin 4.1.16-1(47 票, 2026-05 更新): 上游 Apache-2.0 官方 RPM 二进制重打包"
    "(license=Apache), 安装到 /opt/openoffice4; PKGBUILD 会删除 usr/bin/soffice 符号链接以避免与 "
    "libreoffice-common 冲突 ⇒ 与 LibreOffice 并存不冲突。sizeMiB=388 为 44 个上游 RPM 载荷实测"
    "解包体积。注意: 硬依赖 gtk2 已移出官方仓库(仅 AUR), python2 亦然 —— 手工/助手安装需先满足"
    "这套旧栈依赖。"
)


def mk_app(aid, en, zh, den, dzh, category, aur, size, spdx, tags, order, note):
    return {
        "id": aid,
        "kind": "application",
        "name": {"en": en, "zh_CN": zh},
        "description": {"en": den, "zh_CN": dzh},
        "primaryCategory": category,
        "tags": tags,
        "selection": {"mode": "multi"},
        "provider": "aur",
        "artifact": {"type": "package", "ids": [aur]},
        "scope": "system",
        "source": "aur",
        "license": {
            "classification": "open-source",
            "spdx": spdx,
            "redistributable": True,
            "requiresAcceptance": False,
        },
        "review": {"status": "reviewed", "date": DATE, "note": note},
        "availability": {
            "status": "available",
            "architectures": ["x86_64"],
            "networkRequired": True,
            "offlinePolicy": "online-only",
            "channel": "default",
        },
        "sizeMiB": size,
        "requires": [],
        "recommends": [],
        "conflicts": [],
        "presentation": {"recommended": True, "defaultSelected": False, "order": order},
    }


def main() -> int:
    assert OPENOFFICE_SIZE_MIB, "先填入实测体积再运行(勿提交占位值)"
    cat = json.loads(P.read_text(encoding="utf-8"))
    apps = {a["id"]: a for a in cat["applications"]}
    cats = {c["id"]: c for c in cat["categories"]}
    bundles = {b["id"]: b for b in cat["bundles"]}

    assert "openoffice" not in apps, "openoffice 已是 catalog 条目, 勿重复添加"
    assert "openoffice" not in cats["app-office"]["children"]

    # 1) 新增 OpenOffice 条目(app-office), order 接在该分类现有最大值之后
    order = max(
        a["presentation"]["order"] for a in cat["applications"]
        if a.get("primaryCategory") == "app-office"
    ) + 10
    cat["applications"].append(mk_app(
        "openoffice", "Apache OpenOffice", "Apache OpenOffice",
        "Classic open-source office suite (Writer, Calc, Impress, Base, Draw, Math) shipped as the "
        "upstream binary; installs under /opt/openoffice4.",
        "经典开源办公套件（Writer/Calc/Impress/Base/Draw/Math），上游二进制分发包，"
        "安装到 /opt/openoffice4。",
        "app-office", "openoffice-bin", OPENOFFICE_SIZE_MIB, "Apache-2.0",
        ["office", "third-party"], order, OPENOFFICE_NOTE))

    # 2) 分类 children 与分类根 bundle 的 optional 必须同步(测试硬约束)
    cats["app-office"]["children"].append("openoffice")
    bundles["app-office"]["children"]["optional"] = list(cats["app-office"]["children"])

    # 3) 推荐标: LibreOffice 打开(OnlyOffice 本来就是 true)
    assert apps["libreoffice"]["presentation"]["recommended"] is False
    apps["libreoffice"]["presentation"]["recommended"] = True
    assert apps["onlyoffice"]["presentation"]["recommended"] is True

    # 4) bundle-office-suite: 三件套提到 recommended, optional 清空(原先只有这两件)
    suite = bundles["bundle-office-suite"]
    assert suite["children"]["optional"] == ["libreoffice", "onlyoffice"], suite["children"]["optional"]
    suite["children"]["recommended"] = [
        "genoffice", "libreoffice", "onlyoffice", "openoffice",
        "wordcraft", "gridcraft", "deckcraft", "pdfcraft",
    ]
    suite["children"]["optional"] = []
    suite["description"] = {
        "en": "Workflow-only preset: the office suites (GenOffice, LibreOffice, ONLYOFFICE, "
              "Apache OpenOffice) plus the Craft office apps.",
        "zh_CN": "工作流专用预设：办公套件（GenOffice、LibreOffice、ONLYOFFICE、Apache OpenOffice）"
                 "+ Craft 办公件。",
    }

    out = json.dumps(cat, indent=2, ensure_ascii=False)
    P.write_bytes((out.replace("\n", "\r\n") + "\r\n").encode("utf-8"))
    print(f"写入完成: applications={len(cat['applications'])} bundles={len(cat['bundles'])} "
          f"categories={len(cat['categories'])}; openoffice order={order} "
          f"size={OPENOFFICE_SIZE_MIB}MiB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
