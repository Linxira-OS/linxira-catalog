#!/usr/bin/env python3
"""把 GenOffice + ArtCraft CraftSuite(13) 加入 catalog-v3.json。

路径选择:复用既有机制 —— 这些应用 AUR 全都有(`-bin`),catalog 早已支持 `source: aur`
(brave/onlyoffice 先例),因此**不新增仓库、不自建 PKGBUILD、不加托管**,
只加 catalog 数据 + 打 recommended 标。

sizeMiB = 上游 .deb 的 Installed-Size(KiB/1024,四舍五入),2026-10-14 实测。
写回格式与原文完全一致: json.dumps(indent=2, ensure_ascii=False) + CRLF + 尾换行。
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "catalog" / "catalog-v3.json"
DATE = "2026-10-14"

CRAFT_NOTE = ("AUR {aur}(上游 2026-10 活跃, Apache-2.0); sizeMiB 取自上游 .deb 的 "
              "Installed-Size(2026-10-14 实测)。")
GENOFFICE_NOTE = ("AUR genoffice-bin(2026-10 活跃)。上游主仓 Apache-2.0, 但 ee/ 目录另授 "
                  "GenOffice Enterprise License(禁生产使用, 当前为空) —— **每版发布前需复核 "
                  "ee/ 是否含代码**。sizeMiB 取自上游 .deb 的 Installed-Size。")

# id, en, zh, desc_en, desc_zh, category, aur id, sizeMiB, spdx, tags
APPS = [
    # --- 图形、摄影与 CAD ---------------------------------------------------
    ("photocraft", "PhotoCraft", "图像编辑（Photoshop 类）",
     "Open-source raster image editor in pure Rust: layers, masks, adjustment layers, type and brushes; opens and saves layered PSD/PSB.",
     "纯 Rust 开源位图编辑器（Photoshop 类）：图层、蒙版、调整图层、文字与画笔；可读写分层 PSD/PSB。",
     "app-graphics", "photocraft-bin", 150, "MIT OR Apache-2.0", ["graphics", "photo", "third-party"]),
    ("lightcraft", "LightCraft", "无损修图（Lightroom 类）",
     "Non-destructive photo editor in pure Rust: culling, RAW development and batch export.",
     "纯 Rust 无损修图（Lightroom 类）：挑图、RAW 显影与批量导出。",
     "app-graphics", "lightcraft-bin", 193, "Apache-2.0", ["graphics", "photo", "third-party"]),
    ("vectorcraft", "VectorCraft", "矢量绘图（Illustrator 类）",
     "Open-source vector art tool in pure Rust: shape layers, gradient fills, dashed strokes and SVG.",
     "纯 Rust 开源矢量绘图（Illustrator 类）：形状图层、渐变填充、虚线描边与 SVG。",
     "app-graphics", "vectorcraft-bin", 210, "Apache-2.0", ["graphics", "vector", "third-party"]),
    ("designcraft", "DesignCraft", "排版与版面（InDesign 类）",
     "Page and layout design editor in pure Rust: master pages, text frames and PDF export.",
     "纯 Rust 版面设计编辑器（InDesign 类）：主页、文本框与 PDF 导出。",
     "app-graphics", "designcraft-bin", 141, "Apache-2.0", ["graphics", "layout", "third-party"]),
    ("figcraft", "FigCraft", "界面设计与原型（Figma 类）",
     "Interface design and prototyping in pure Rust: infinite canvas, components and handoff.",
     "纯 Rust 界面设计与原型（Figma 类）：无限画布、组件与交付标注。",
     "app-graphics", "figcraft", 168, "Apache-2.0", ["graphics", "ui", "third-party"]),
    ("cadcraft", "CADCraft", "CAD 制图（AutoCAD 类）",
     "Computer-aided design and drafting in pure Rust: parametric 2D/3D modeling.",
     "纯 Rust CAD 制图（AutoCAD 类）：参数化 2D/3D 建模。",
     "app-graphics", "cadcraft-bin", 114, "Apache-2.0", ["graphics", "cad", "third-party"]),
    # --- 视频与音频创作 -----------------------------------------------------
    ("filmcraft", "FilmCraft", "视频剪辑（Premiere 类）",
     "Open-source non-linear video editor in pure Rust: timeline, multicam, color and audio, with delivery exports.",
     "纯 Rust 开源非线性剪辑（Premiere 类）：时间线、多机位、调色与音频，含交付导出。",
     "app-creation", "filmcraft-bin", 137, "Apache-2.0", ["video", "editing", "third-party"]),
    ("effectcraft", "EffectCraft", "视觉特效（After Effects 类）",
     "Motion graphics and compositing in pure Rust: keyframes, tracking, masks and a render queue.",
     "纯 Rust 动态图形与合成（After Effects 类）：关键帧、跟踪、蒙版与渲染队列。",
     "app-creation", "effectcraft-bin", 146, "Apache-2.0", ["video", "vfx", "third-party"]),
    ("soundcraft", "SoundCraft", "音频工作站（Pro Tools 类）",
     "Open-source digital audio workstation in pure Rust: multitrack recording, editing and mixing.",
     "纯 Rust 开源数字音频工作站（Pro Tools 类）：多轨录制、编辑与混音。",
     "app-creation", "soundcraft-bin", 37, "Apache-2.0", ["audio", "daw", "third-party"]),
    # --- 办公 ---------------------------------------------------------------
    ("genoffice", "GenOffice", "AI 办公套件（Office 替代）",
     "AI-native office suite: Docs, Sheets, Slides, PDF, HTML and Markdown editors with a built-in AI panel, plus a `genoffice` CLI and agent skill; bring your own API key.",
     "AI 原生办公套件：文档/表格/幻灯片/PDF/HTML/Markdown 六个编辑器 + 内置 AI 面板，另带 `genoffice` CLI 与 agent 技能；自带 API Key。",
     "app-office", "genoffice-bin", 545, "Apache-2.0", ["office", "ai", "third-party"]),
    ("wordcraft", "WordCraft", "文字处理（Word 类）",
     "Clean-room reimplementation of Microsoft Word in pure Rust: opens and saves .docx with styles, tables and tracked changes.",
     "纯 Rust 净室重写（Word 类）：读写 .docx，含样式、表格与修订。",
     "app-office", "wordcraft-bin", 169, "Apache-2.0", ["office", "document", "third-party"]),
    ("gridcraft", "GridCraft", "电子表格（Excel 类）",
     "Clean-room spreadsheet in pure Rust: opens and saves .xlsx and CSV/TSV with formulas and charts.",
     "纯 Rust 净室电子表格（Excel 类）：读写 .xlsx 与 CSV/TSV，含公式与图表。",
     "app-office", "gridcraft-bin", 45, "Apache-2.0", ["office", "spreadsheet", "third-party"]),
    ("deckcraft", "DeckCraft", "演示文稿（PowerPoint 类）",
     "Clean-room reimplementation of Microsoft PowerPoint in pure Rust: layouts, speaker notes and present mode for .pptx.",
     "纯 Rust 净室重写（PowerPoint 类）：.pptx 版式、演讲者备注与放映模式。",
     "app-office", "deckcraft-bin", 145, "Apache-2.0", ["office", "presentation", "third-party"]),
    # --- 文档与阅读 ---------------------------------------------------------
    ("pdfcraft", "PDFCraft", "PDF 阅读与编辑（Acrobat 类）",
     "Open-source PDF reader and editor in pure Rust: annotation, forms and page operations, plus a CLI converter.",
     "纯 Rust 开源 PDF 阅读与编辑（Acrobat 类）：批注、表单与页面操作，另含 CLI 转换器。",
     "app-documents", "pdfcraft-bin", 157, "Apache-2.0", ["pdf", "document", "third-party"]),
]


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


def mk_bundle(bid, en, zh, den, dzh, category, tags, required, recommended, optional, order):
    return {
        "id": bid,
        "kind": "bundle",
        "surface": "applications",
        "name": {"en": en, "zh_CN": zh},
        "description": {"en": den, "zh_CN": dzh},
        "primaryCategory": category,
        "tags": tags,
        "selection": {"mode": "preset"},
        "children": {"required": required, "recommended": recommended, "optional": optional},
        "criticalSystemCapability": False,
        "presentation": {"defaultSelected": False, "order": order},
    }


def main():
    raw = P.read_bytes()
    cat = json.loads(raw.decode("utf-8"))
    apps = {a["id"]: a for a in cat["applications"]}
    cats = {c["id"]: c for c in cat["categories"]}
    bundles = {b["id"]: b for b in cat["bundles"]}

    for t in APPS:
        assert t[0] not in apps, f"已是 catalog 条目: {t[0]}"
    for bid in ("bundle-creative-suite", "bundle-office-suite"):
        assert bid not in bundles, f"已存在: {bid}"

    # 每个分类内 order 从现有最大值起递增
    next_order = {}
    for cid, c in cats.items():
        vals = [apps[i]["presentation"]["order"] for i in c.get("children", []) if i in apps]
        next_order[cid] = max(vals) if vals else 0

    for (aid, en, zh, den, dzh, cid, aur, size, spdx, tags) in APPS:
        note = GENOFFICE_NOTE if aid == "genoffice" else CRAFT_NOTE.format(aur=aur)
        next_order[cid] += 10
        cat["applications"].append(
            mk_app(aid, en, zh, den, dzh, cid, aur, size, spdx, tags, next_order[cid], note))
        cats[cid]["children"].append(aid)

    # 分类根 bundle 的 optional 必须与 category.children 同步(测试硬约束)
    for cid in sorted({t[5] for t in APPS}):
        b = bundles[cid]
        b["children"]["optional"] = list(cats[cid]["children"])

    # 办公推荐位: GenOffice 标推荐, LibreOffice 保留但降为不推荐
    assert apps["libreoffice"]["presentation"]["recommended"] is True
    apps["libreoffice"]["presentation"]["recommended"] = False

    cat["bundles"].extend([
        mk_bundle(
            "bundle-creative-suite", "Creative suite (Craft App Suite)", "创意套件（Craft App Suite）",
            "Workflow-only preset: the Craft App suite for photo, vector, layout, video, audio and VFX work; office apps live in the office bundle.",
            "工作流专用预设：修图/矢量/排版/剪辑/音频/特效所需的 Craft App 套装；办公类见办公套件预设。",
            "app-graphics", ["workflow-only", "creative", "third-party"],
            [], ["photocraft", "vectorcraft", "filmcraft", "designcraft"],
            ["lightcraft", "effectcraft", "soundcraft", "figcraft", "cadcraft"], 2),
        mk_bundle(
            "bundle-office-suite", "Office suite", "办公套件",
            "Workflow-only preset: AI office (GenOffice) plus the Craft office apps; LibreOffice/OnlyOffice stay optional.",
            "工作流专用预设：AI 办公（GenOffice）+ Craft 办公件；LibreOffice/OnlyOffice 保持可选。",
            "app-office", ["workflow-only", "office", "third-party"],
            [], ["genoffice", "wordcraft", "gridcraft", "deckcraft", "pdfcraft"],
            ["libreoffice", "onlyoffice"], 3),
    ])

    out = json.dumps(cat, indent=2, ensure_ascii=False)
    P.write_bytes((out.replace("\n", "\r\n") + "\r\n").encode("utf-8"))
    print(f"写入完成: applications={len(cat['applications'])} bundles={len(cat['bundles'])}"
          f" categories={len(cat['categories'])} bytes={len(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
