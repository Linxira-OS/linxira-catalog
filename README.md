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

## Offline policy (installation surfaces)

`availability.offlinePolicy` drives the badge every installation surface
(installer, Package Center, Component Manager) must display, so users can
distinguish what ships on the media from what needs a network:

| value | badge | meaning |
|---|---|---|
| `included` | 镜像自带 | Package is carried in the ISO offline repository; installs without network. |
| `online-only` | 需联网 | Package is not on the media; a network is required. |
| `defer-with-consent` | 可选延后 | Defaults to deferred; installs online after explicit user consent. |

Installer-eligible leaves additionally require `review.status == "reviewed"`;
leaves still in review must never be default-selected.

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

---

## 简体中文

Linxira Catalog —— 面向 Linxira OS 的规范化、带版本的软件组件元数据。

Catalog v3 是面向全新安装器、Package Center 与 Bundle/Component Manager 工作的规范图。Catalog v2 保持不变，作为现有消费者的兼容输入。软件包事务仍由经过审计的规划与事务后端负责。

Catalog v3 在共享稳定 ID 与同一选择模型的同时，划分出三个产品面：

- `desktops[]` 包含经过评审、互斥的桌面组合。
- `applications[]` 包含可单独选择的普通软件。
- `components[]` 包含运行时、工具与系统功能。
- `bundles[]` 是可展开的预设，具有显式的 `desktops`、`applications` 或 `components` 表面，以及 `required`、`recommended`、`optional` 引用。Bundle 可嵌套其他 bundle，且必须构成 DAG。
- 每个 desktop 或 applications 类别都有一个同 ID 的类别根 bundle，其成员按顺序恰好镜像该类别的子项，全部作为 optional 引用。
- `operations[]` 包含固定的受控操作 ID。目录数据永远不包含可执行的 shell 字符串。
- `categories[]` 通过恰好一个 `primaryCategory` 持有每个 desktop、application、component 或 bundle；application 类别可多选，而桌面环境类别可互斥。
- Bundle 声明 `preset`；选择预设会改变叶子的默认值，但不会创建不透明的安装工件。

相同的稳定 ID 必须被安装器、已安装的管理器、计划、回执与 CLI 交接共同使用。选择与回执以叶子 ID 为键，而非树路径。Catalog v2 的 `profiles[]` 仅作兼容保留，绝不能用作 v3 的能力模型。

## 信任模型

- 每个来源声明其包生态与信任等级。
- Miniforge 通道是显式来源：`conda-forge` 与 `bioconda` 是经验证的第三方通道，基础系统从不默认启用。
- 每个叶子声明 provider、artifact、scope、source、license、review、availability、offline policy、size 与依赖元数据。
- 外部生态默认禁用，需要用户显式选择加入。
- 待定的专有或第三方候选保留在可选评审通道中，绝不会被默认选中。
- 目录数据只包含包标识符，绝不包含可执行命令字符串。
- Profile ID 是允许列表中的事务请求，而非 shell 片段。

## 离线策略（安装面）

`availability.offlinePolicy` 驱动每个安装面（安装器、Package Center、组件管理器）必须显示的徽标，用户据此区分介质自带与需要联网的内容：

| 值 | 徽标 | 含义 |
|---|---|---|
| `included` | 镜像自带 | 包随 ISO 离线仓库提供；无需联网即可安装。 |
| `online-only` | 需联网 | 包不在介质上；需要网络。 |
| `defer-with-consent` | 可选延后 | 默认延后；在用户显式同意后在线安装。 |

安装器可选叶子还要求 `review.status == "reviewed"`；仍在评审中的叶子绝不能被默认选中。

## 文件

- `catalog/catalog-v2.json`：当前已评审目录
- `schema/catalog-v2.schema.json`：JSON Schema Draft 2020-12 契约
- `catalog/catalog-v3.json`：application/component/bundle 图
- `schema/catalog-v3.schema.json`：严格的 v3 JSON Schema Draft 2020-12 契约
- `tests/test_catalog_v3.py`：schema 与语义校验

安装开发依赖并运行：

```sh
python -m unittest discover -s tests -v
```

校验覆盖 schema、类别根 ID 对与所有其他全局 ID、引用、primary-category 归属、bundle 表面、嵌套 bundle 无环性、重复成员、provider/source 边界、浏览器应用的 reviewed 默认值、评审通道策略、打印/扫描能力覆盖以及目录所用的选择模式。
