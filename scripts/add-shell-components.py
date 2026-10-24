#!/usr/bin/env python3
"""把 bash 之外的三个 shell 作为 components 条目加入 catalog（幂等）。

背景: welcome 的「终端」页按需安装 shell, 安装必须复用 linxira-components 的
plan → confirm → apply 通道, 而该通道只认 catalog 条目 ⇒ 先有数据条目, 再有页面。

设计口径(2026-10-24):
- bash 不在此列表: 它是基线, 所有镜像都自带, 也是默认登录 shell。
- 顺序 fish → nushell → zsh(字母序), 对应 presentation.order 1..3。
- 全部 networkRequired=true / offlinePolicy=online-only: 镜像不预装, 装完系统后按需下载。
- installerVisible=true: 安装器与 welcome 用的是同一份 catalog, 两边都能看到。
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "catalog-v3.json"

SHELLS = [
    {
        "id": "component-fish",
        "kind": "component",
        "name": {"en": "fish shell", "zh_CN": "fish shell"},
        "description": {
            "en": "Friendly interactive shell: syntax highlighting, autosuggestions and a rich prompt out of the box.",
            "zh_CN": "友好的交互式 shell：语法高亮、自动建议与开箱即用的提示符。",
        },
        "primaryCategory": "cap-terminal",
        "tags": ["shell", "terminal"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {"type": "package", "ids": ["fish"]},
        "scope": "system",
        "source": "arch",
        "license": {
            "classification": "open-source",
            "spdx": "GPL-2.0-only",
            "redistributable": True,
            "requiresAcceptance": False,
        },
        "review": {"status": "reviewed", "date": "2026-10-24"},
        "availability": {
            "status": "available",
            "architectures": ["x86_64"],
            "networkRequired": True,
            "offlinePolicy": "online-only",
            "channel": "default",
        },
        "sizeMiB": 18,
        "requires": [],
        "recommends": [],
        "conflicts": [],
        "presentation": {
            "recommended": False,
            "defaultSelected": False,
            "order": 1,
            "installerVisible": True,
        },
        "criticalSystemCapability": False,
    },
    {
        "id": "component-nushell",
        "kind": "component",
        "name": {"en": "Nushell", "zh_CN": "Nushell"},
        "description": {
            "en": "Structured-data shell: pipelines operate on typed tables instead of raw text.",
            "zh_CN": "结构化数据 shell：管道处理的是带类型的表格而不是纯文本。",
        },
        "primaryCategory": "cap-terminal",
        "tags": ["shell", "terminal"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {"type": "package", "ids": ["nushell"]},
        "scope": "system",
        "source": "arch",
        "license": {
            "classification": "open-source",
            "spdx": "MIT",
            "redistributable": True,
            "requiresAcceptance": False,
        },
        "review": {"status": "reviewed", "date": "2026-10-24"},
        "availability": {
            "status": "available",
            "architectures": ["x86_64"],
            "networkRequired": True,
            "offlinePolicy": "online-only",
            "channel": "default",
        },
        "sizeMiB": 210,
        "requires": [],
        "recommends": [],
        "conflicts": [],
        "presentation": {
            "recommended": False,
            "defaultSelected": False,
            "order": 2,
            "installerVisible": True,
        },
        "criticalSystemCapability": False,
    },
    {
        "id": "component-zsh",
        "kind": "component",
        "name": {"en": "Zsh", "zh_CN": "Zsh"},
        "description": {
            "en": "POSIX-compatible extended shell with a very large configuration ecosystem.",
            "zh_CN": "兼容 POSIX 的扩展 shell，配置生态庞大。",
        },
        "primaryCategory": "cap-terminal",
        "tags": ["shell", "terminal"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {"type": "package", "ids": ["zsh"]},
        "scope": "system",
        "source": "arch",
        "license": {
            "classification": "open-source",
            "spdx": "MIT",
            "redistributable": True,
            "requiresAcceptance": False,
        },
        "review": {"status": "reviewed", "date": "2026-10-24"},
        "availability": {
            "status": "available",
            "architectures": ["x86_64"],
            "networkRequired": True,
            "offlinePolicy": "online-only",
            "channel": "default",
        },
        "sizeMiB": 7,
        "requires": [],
        "recommends": [],
        "conflicts": [],
        "presentation": {
            "recommended": False,
            "defaultSelected": False,
            "order": 3,
            "installerVisible": True,
        },
        "criticalSystemCapability": False,
    },
]


def main() -> int:
    raw = CATALOG.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    catalog = json.loads(raw.decode("utf-8"))

    ids = {c["id"] for c in catalog["components"]}
    for shell in SHELLS:
        if shell["id"] in ids:
            print(f"skip {shell['id']} (exists)")
            continue
        catalog["components"].append(shell)
        print(f"add {shell['id']}")

    category = next(c for c in catalog["categories"] if c["id"] == "cap-terminal")
    root = next(b for b in catalog["bundles"] if b["id"] == "cap-terminal")
    for shell in SHELLS:
        for seq in (category["children"], root["children"]["optional"]):
            if shell["id"] not in seq:
                seq.append(shell["id"])

    CATALOG.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + newline, encoding="utf-8"
    )
    print("catalog written:", CATALOG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
