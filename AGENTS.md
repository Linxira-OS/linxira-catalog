# linxira-catalog · Agent 开发规范

> **档位**:A 档 · 系统源仓(带 `VERSION` + `.github/workflows/release.yml`)。
> **本仓职责**:Linxira OS 的规范化、带版本的软件组件元数据(catalog v2 / v3 schema 与数据)唯一来源。
> 通用条款见工作区总纲 `f:\Linxira-OS\AGENTS.md`;发布/测试口径见 `linxira-os/docs/RELEASE_STANDARD.md`。本文件只写本仓特有约定。

## 职责与边界

- **负责**:`catalog/catalog-v2.json`、`catalog/catalog-v3.json` 数据,`schema/*.schema.json`(JSON Schema Draft 2020-12 契约),以及排序/同步脚本 `scripts/`。
- **v3 模型**:`desktops[]` / `applications[]` / `components[]` / `bundles[]`(可嵌套,必须构成 DAG)/ `operations[]`(固定受控操作 ID)/ `categories[]`。稳定 ID 被安装器、已安装管理器、计划、回执与 CLI 共同使用。
- **不负责**:包事务的规划与执行(归 `linxira-components`);任何可执行命令字符串。目录数据**只含包标识符,绝不包含 shell 命令**。
- 与 `linxira-components`、`linxira-component-manager`、`linxira-completion-agent`、`linxira-config-hub`、安装器的边界:它们消费本仓 schema 与数据,本仓不消费它们。

## 目录布局

```
catalog/catalog-v2.json        当前已评审目录(v2 兼容输入)
catalog/catalog-v3.json        application/component/bundle 图
schema/catalog-v2.schema.json  v2 契约
schema/catalog-v3.schema.json  严格 v3 契约
scripts/add-desktops.py        目录脚本
scripts/sync-offline-policy.py 离线策略同步脚本
release_locks.py               发布锁定辅助
tests/test_catalog_v3.py       schema 与语义校验
requirements-dev.txt
```

## 本地校验

```sh
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v     # schema + 语义校验(见 README)
```

CI(`.github/workflows/ci.yml`)另跑:`PYTHONPATH=src python -m unittest discover -s tests -v` 与 `python -m compileall -q src`(Python 3.13)。

校验覆盖:schema、类别根 ID 对与全局 ID、引用、primary-category 归属、bundle 表面、嵌套无环性、重复成员、provider/source 边界、reviewed 默认值、评审通道策略、打印/扫描能力覆盖与选择模式。

## 版本与发布

- 版本唯一来源是根目录 `VERSION`(当前 3.2.8)。
- 提交 `VERSION` 变更即触发 `.github/workflows/release.yml` 建 `v<VERSION>` Release,再由 `packages/auto-bump.yml` 走全自动发布链。**禁止手工 bump 或手工改 PKGBUILD**。

## 禁区

- **目录数据不得含可执行命令**;`operations[]` 只放固定受控操作 ID,`profile ID` 是允许列表中的事务请求而非 shell 片段。
- 外部生态(AUR/Conda/专有)默认禁用,需显式 opt-in;待评审候选保留在 review 通道,**绝不默认选中**。
- 离线策略徽标(`included` / `online-only` / `defer-with-consent`)是安装面必须显示的口径,不得私改语义。
- 保持 v2 兼容输入不被破坏;不要用 v3 的能力模型替换 v2 `profiles[]`。
- 破坏性操作(删叶子/改稳定 ID)先确认,ID 变更会波及所有下游消费者。