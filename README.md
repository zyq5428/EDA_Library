# EDA_Library

面向个人硬件开发者的 Cadence 24.1 器件库框架。使用 **OrCAD X Capture CIS 的 Component Explorer 管理完整器件**，使用 PCB Editor / Padstack Editor 编辑物理模型；本仓库保存可移植的库文件、器件索引与检查记录。

当前仅包含框架，尚无已验证的实际器件或原生 Cadence 库文件。目录中的 README 不是可直接加载的器件库。

## 开始使用

1. 克隆本仓库到固定目录，例如 `D:/EDA_Library`。
2. 按 [Cadence 24.1 配置说明](docs/cadence-24.1-setup.md) 设置封装、焊盘和 STEP 搜索路径。
3. 按 [第一个器件入库指南](docs/quickstart.md) 建立一个完整器件，关联符号、封装和参数。
4. 完成 [入库检查表](templates/component-review.md)，记录结果，然后更新 [器件清单](parts.csv)。
5. 运行 `python scripts/validate_library.py`，提交 Git；如需云端修订管理，再发布到自己的 Cloud Workspace。

检查脚本需要 Python 3.9 或更高版本；Linux / macOS 上命令通常为 `python3 scripts/validate_library.py`。

## 目录

```text
EDA_Library/
├── capture/          # 已入库的 Capture .olb
├── footprints/       # 已入库的封装 .dra + .psm；初期采用扁平目录
├── padstacks/        # 已入库的 .pad
├── step/             # 可选 .step / .stp
├── incoming/         # 第三方原始资料、待核对模型；不加入正式搜索路径
├── docs/
│   ├── components/   # 每个器件的来源、核对和实板验证记录
│   └── ...           # 配置、命名、入库与版本管理说明
├── templates/        # 器件记录、检查表、目录分类模板
├── scripts/          # 无第三方依赖的器件清单检查脚本
├── parts.csv         # 器件索引；不是可直接加载的 CIS 数据库
└── .github/workflows/ # 自动检查器件清单和文件关联
```

## 管理边界

- Component Explorer：器件分类、参数、符号与封装关联、器件放置。
- Git：本地模型与文档的版本、备份和项目版本标签。
- Cloud Workspace：可选的发布、同步和修订管理；本地 Workspace 不等同于云端修订管理。
- `parts.csv`：便于审核和迁移的索引。它不会自动同步到 Component Explorer，也不是 `.dbc`；CIS ODBC 需要另行建立数据库和字段映射。
- 检查脚本只验证 CSV、文件存在性及命名关联，**不能验证焊盘尺寸、引脚电气映射或 Cadence 二进制内容**。

## 文档

- [Cadence 24.1 配置](docs/cadence-24.1-setup.md)
- [第一个器件入库](docs/quickstart.md)
- [命名与绘图约定](docs/library-conventions.md)
- [清单字段与验证规则](docs/catalog-schema.md)
- [版本、备份与项目复现](docs/versioning.md)
- [第三方来源与许可](docs/sources-and-licensing.md)
- [GitHub SSH 配置](docs/github-ssh.md)

## 官方参考

- [OrCAD X 器件库创建与管理](https://www5.cadence.com/library-creation.html)
- [OrCAD X Capture CIS 24.1 Workspace 管理](https://resources.pcb.cadence.com/orcad-x-data-management-faqs/how-to-create-and-manage-workspaces-in-orcad-x-capture-cis-241)
- [从 Component Explorer 发布器件](https://community.cadence.com/cadence_technology_forums/pcb-design/f/allegro-x-capture-cis/59099/sharing-a-component-in-the-shared-workspace)
- [从 PCB 导出封装库](https://community.cadence.com/cadence_technology_forums/pcb-design/f/pcb-design/11515/exporting-saving-footprints-from-brd-file)
