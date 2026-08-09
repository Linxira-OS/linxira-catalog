#!/usr/bin/env python3
"""Expand catalog desktops section with multi-desktop support + rich zh/en descriptions.

Adds Xfce4 / Hyprland / Sway / Cosmic, releases GNOME, and enriches every
desktop entry with a detailed Chinese/English description (matching CachyOS's
netinstall description quality). New desktops are online-only (packages not on
the ISO); Plasma stays the included default.
"""
import json
import sys

PATH = r'F:/Linxira-OS/linxira-catalog/catalog/catalog-v3.json'

DESKTOPS = [
    {
        "id": "desktop-plasma",
        "kind": "desktop",
        "name": {"en": "KDE Plasma", "zh_CN": "KDE Plasma"},
        "description": {
            "en": "KDE Plasma 6 - the Linxira default desktop. A modern, full-featured desktop that balances "
                 "polish, customization and performance. Ships on the ISO, so it works offline and needs no "
                 "additional download. Includes Dolphin file manager, Konsole terminal, Kate editor, "
                 "System Settings, Spectacle screenshots and KDE Discover software center.",
            "zh_CN": "KDE Plasma 6——Linxira 默认桌面。功能全面、外观精致且高度可定制，兼顾美观与性能。"
                     "随镜像附带，离线即可使用，无需额外下载。包含 Dolphin 文件管理器、Konsole 终端、"
                     "Kate 编辑器、系统设置、Spectacle 截图和 KDE Discover 软件中心。"
        },
        "primaryCategory": "desktop-environments",
        "tags": ["desktop", "kde", "plasma"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {
            "type": "package",
            "ids": [
                "bluedevil", "dolphin", "kdialog", "kinfocenter", "kscreen",
                "konsole", "kate", "plasma-desktop", "plasma-nm", "plasma-pa",
                "plasma-workspace", "plasma-systemmonitor", "spectacle",
                "systemsettings", "polkit-kde-agent",
            ],
        },
        "scope": "system",
        "source": "arch",
        "license": {"classification": "open-source", "spdx": "GPL-2.0-or-later",
                    "redistributable": True, "requiresAcceptance": False},
        "review": {"status": "reviewed", "date": "2026-07-20"},
        "availability": {"status": "available", "architectures": ["x86_64"],
                         "networkRequired": False, "offlinePolicy": "included",
                         "channel": "default"},
        "sizeMiB": 2048,
        "requires": [], "recommends": [], "conflicts": ["desktop-gnome", "desktop-xfce",
                                                       "desktop-hyprland", "desktop-sway",
                                                       "desktop-cosmic"],
        "presentation": {"recommended": True, "defaultSelected": True, "order": 1},
    },
    {
        "id": "desktop-gnome",
        "kind": "desktop",
        "name": {"en": "GNOME", "zh_CN": "GNOME"},
        "description": {
            "en": "GNOME 48 - a clean, minimalist desktop focused on simplicity and focus. "
                 "Designed to put you in control and get things done with a calm, "
                 "uncluttered workflow. Uses the modern GNOME Shell with its overview, "
                 "Activities and integrated search. Requires an internet connection to install.",
            "zh_CN": "GNOME 48——简洁极致的现代桌面，以专注与简单为核心。采用 GNOME Shell 的"
                     "活动概览、全局搜索与集成工作流，界面清爽、上手轻松。需要联网安装。"
        },
        "primaryCategory": "desktop-environments",
        "tags": ["desktop", "gnome"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {
            "type": "package",
            "ids": [
                "file-roller", "gnome-control-center", "gnome-disk-utility",
                "gnome-keyring", "gnome-session", "gnome-shell", "gnome-text-editor",
                "gnome-tweaks", "gdm", "ptyxis",
            ],
        },
        "scope": "system",
        "source": "arch",
        "license": {"classification": "open-source", "spdx": "GPL-2.0-or-later",
                    "redistributable": True, "requiresAcceptance": False},
        "review": {"status": "reviewed", "date": "2026-08-09"},
        "availability": {"status": "available", "architectures": ["x86_64"],
                         "networkRequired": True, "offlinePolicy": "online-only",
                         "channel": "default"},
        "sizeMiB": 1400,
        "requires": [], "recommends": [], "conflicts": ["desktop-plasma", "desktop-xfce",
                                                       "desktop-hyprland", "desktop-sway",
                                                       "desktop-cosmic"],
        "presentation": {"recommended": False, "defaultSelected": False, "order": 2},
    },
    {
        "id": "desktop-xfce",
        "kind": "desktop",
        "name": {"en": "Xfce", "zh_CN": "Xfce"},
        "description": {
            "en": "Xfce 4.20 - a lightweight desktop for UNIX-like systems. Fast, low on "
                 "system resources and visually appealing, ideal for older hardware or "
                 "users who prefer a classic, snappy workflow. Uses the LightDM greeter. "
                 "Requires an internet connection to install.",
            "zh_CN": "Xfce 4.20——轻量级桌面环境，快速、省资源且观感友好，适合老硬件或偏爱"
                     "经典流畅工作流的用户。使用 LightDM 登录管理器。需要联网安装。"
        },
        "primaryCategory": "desktop-environments",
        "tags": ["desktop", "xfce", "lightweight"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {
            "type": "package",
            "ids": [
                "xfce4", "xfce4-goodies", "xfce4-terminal", "thunar",
                "lightdm", "lightdm-gtk-greeter", "blueman", "file-roller",
                "galculator", "gvfs",
            ],
        },
        "scope": "system",
        "source": "arch",
        "license": {"classification": "open-source", "spdx": "GPL-2.0-or-later",
                    "redistributable": True, "requiresAcceptance": False},
        "review": {"status": "reviewed", "date": "2026-08-09"},
        "availability": {"status": "available", "architectures": ["x86_64"],
                         "networkRequired": True, "offlinePolicy": "online-only",
                         "channel": "default"},
        "sizeMiB": 900,
        "requires": [], "recommends": [], "conflicts": ["desktop-plasma", "desktop-gnome",
                                                       "desktop-hyprland", "desktop-sway",
                                                       "desktop-cosmic"],
        "presentation": {"recommended": False, "defaultSelected": False, "order": 3},
    },
    {
        "id": "desktop-hyprland",
        "kind": "desktop",
        "name": {"en": "Hyprland", "zh_CN": "Hyprland"},
        "description": {
            "en": "Hyprland - a highly customizable dynamic tiling Wayland compositor with "
                 "beautiful animations and window effects. Built for power users who love "
                 "keyboard-driven, scriptable workflows. Ships with Kitty terminal and a "
                 "batteries-included dotfile set. Requires an internet connection to install.",
            "zh_CN": "Hyprland——高度可定制的动态平铺 Wayland 合成器，动画细腻、窗口特效出众。"
                     "专为热爱键盘驱动与脚本化工作流的进阶用户打造，附带 Kitty 终端与开箱即用的"
                     "配置文件。需要联网安装。"
        },
        "primaryCategory": "desktop-environments",
        "tags": ["desktop", "hyprland", "wayland", "tiling"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {
            "type": "package",
            "ids": [
                "hyprland", "kitty", "waybar", "rofi", "hyprpaper",
                "xdg-desktop-portal-hyprland", "sddm", "wl-clipboard",
                "grim", "slurp",
            ],
        },
        "scope": "system",
        "source": "arch",
        "license": {"classification": "open-source", "spdx": "BSD-3-Clause",
                    "redistributable": True, "requiresAcceptance": False},
        "review": {"status": "reviewed", "date": "2026-08-09"},
        "availability": {"status": "available", "architectures": ["x86_64"],
                         "networkRequired": True, "offlinePolicy": "online-only",
                         "channel": "default"},
        "sizeMiB": 700,
        "requires": [], "recommends": [], "conflicts": ["desktop-plasma", "desktop-gnome",
                                                       "desktop-xfce", "desktop-sway",
                                                       "desktop-cosmic"],
        "presentation": {"recommended": False, "defaultSelected": False, "order": 4},
    },
    {
        "id": "desktop-sway",
        "kind": "desktop",
        "name": {"en": "Sway", "zh_CN": "Sway"},
        "description": {
            "en": "Sway - an i3-compatible tiling Wayland compositor. Minimal, stable and "
                 "configurable through plain text files. Perfect for users coming from "
                 "i3 or anyone who wants a distraction-free, keyboard-first desktop. "
                 "Requires an internet connection to install.",
            "zh_CN": "Sway——兼容 i3 的平铺式 Wayland 合成器。极简、稳定，纯文本配置，"
                     "适合 i3 老用户或追求无干扰键盘流桌面的人。需要联网安装。"
        },
        "primaryCategory": "desktop-environments",
        "tags": ["desktop", "sway", "wayland", "i3", "tiling"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {
            "type": "package",
            "ids": [
                "sway", "swaybg", "swaylock", "swayidle", "foot",
                "waybar", "grim", "slurp", "wl-clipboard",
                "xdg-desktop-portal-wlr",
            ],
        },
        "scope": "system",
        "source": "arch",
        "license": {"classification": "open-source", "spdx": "MIT",
                    "redistributable": True, "requiresAcceptance": False},
        "review": {"status": "reviewed", "date": "2026-08-09"},
        "availability": {"status": "available", "architectures": ["x86_64"],
                         "networkRequired": True, "offlinePolicy": "online-only",
                         "channel": "default"},
        "sizeMiB": 500,
        "requires": [], "recommends": [], "conflicts": ["desktop-plasma", "desktop-gnome",
                                                       "desktop-xfce", "desktop-hyprland",
                                                       "desktop-cosmic"],
        "presentation": {"recommended": False, "defaultSelected": False, "order": 5},
    },
    {
        "id": "desktop-cosmic",
        "kind": "desktop",
        "name": {"en": "COSMIC", "zh_CN": "COSMIC"},
        "description": {
            "en": "COSMIC - System76's modern Rust-based desktop environment with advanced "
                 "features, a responsive tiling layout and a calm, configurable UI. A "
                 "fresh take on the Linux desktop with excellent Wayland support. "
                 "Requires an internet connection to install.",
            "zh_CN": "COSMIC——System76 用 Rust 打造的现代化桌面环境，功能先进、支持响应式"
                     "平铺布局，界面沉稳可定制，Wayland 支持出色，是 Linux 桌面的一股新势力。"
                     "需要联网安装。"
        },
        "primaryCategory": "desktop-environments",
        "tags": ["desktop", "cosmic", "rust", "wayland"],
        "selection": {"mode": "multi"},
        "provider": "pacman",
        "artifact": {
            "type": "package",
            "ids": ["cosmic", "cosmic-session"],
        },
        "scope": "system",
        "source": "arch",
        "license": {"classification": "open-source", "spdx": "GPL-3.0-or-later",
                    "redistributable": True, "requiresAcceptance": False},
        "review": {"status": "reviewed", "date": "2026-08-09"},
        "availability": {"status": "available", "architectures": ["x86_64"],
                         "networkRequired": True, "offlinePolicy": "online-only",
                         "channel": "default"},
        "sizeMiB": 900,
        "requires": [], "recommends": [], "conflicts": ["desktop-plasma", "desktop-gnome",
                                                       "desktop-xfce", "desktop-hyprland",
                                                       "desktop-sway"],
        "presentation": {"recommended": False, "defaultSelected": False, "order": 6},
    },
]


def main() -> int:
    catalog = json.loads(open(PATH, encoding="utf-8").read())
    existing = {d["id"]: d for d in catalog.get("desktops", [])}
    for d in DESKTOPS:
        existing[d["id"]] = d
    catalog["desktops"] = [existing[i] for i in existing]  # keep order stable-ish
    open(PATH, "w", encoding="utf-8").write(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    )
    print("desktops now:", [d["id"] for d in catalog["desktops"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
