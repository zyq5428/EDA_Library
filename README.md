# EDA_Library

个人使用的 Cadence 24.1 离线器件库。原理图、封装、焊盘和 3D 模型统一存放，不按来源项目划分子库。

当前包含 **LIB_COMMON.OLB 的 61 个原理图符号、117 个可放置封装、447 个焊盘和 42 个 STEP/STP 模型**。共 155 个 DRA、31 个 SSM、12 个 FSM；`parts.csv` 共 246 条 draft，包含已有 143 条草稿、新增 42 条封装记录和 61 条符号记录。封装记录与符号记录是模型索引，不代表 246 个完整采购器件。

本次保留 `LIB_COMMON.OLB` 与 FPX 原生文件的名称及字节，未修改符号属性、几何或引脚。47 个符号通过内部同名文本找到唯一封装候选；13 个未找到，1 个涉及同名冲突。候选关联已登记到清单，仍须在 Capture 中确认 `PCB Footprint` 和引脚对应。

## Windows 使用

将整个目录复制到例如 `D:/EDA_Library`。PCB Editor 的库路径增加：

```text
psmpath: D:/EDA_Library/footprints
padpath: D:/EDA_Library/padstacks
steppath: D:/EDA_Library/step
```

Capture 中通过 `Place → Part → Add Library` 添加 `D:/EDA_Library/capture/LIB_COMMON.OLB`。符号的 `PCB Footprint` 使用 [完整封装索引](reports/library-footprints.csv) 中的名称，不带路径和 `.psm`。已有 OLB 未自动改写；清单匹配结果用于核对属性。

FPX 的 `SOT23-5` 与已有同名模型内容不同，新版本保存在 `alternatives/sot23-5/`。默认搜索路径使用已有版本；先在 Cadence 中另存为唯一封装名并重新生成 PSM，才能将新版本加入共享库。不要把这两个同名目录同时加入搜索路径。RT9013-33GB 的关联因此暂留空。

## 目录与入口

| 目录 / 文件 | 用途 |
| --- | --- |
| `capture/LIB_COMMON.OLB` | 原始个人原理图器件库 |
| `footprints/` | DRA、PSM、SSM、FSM |
| `padstacks/` | PAD 支持文件 |
| `step/` | 42 个原始 3D 模型 |
| `projects/Hero.fpx` | Footprint Expert 工程 |
| `projects/exports/` | 原始生成脚本、参数、批处理、3D 缓存与日志，保留相对目录 |
| `alternatives/` | 同名冲突的备用模型，不在默认搜索路径中 |
| [parts.csv](parts.csv) | 246 条草稿索引；不是 CIS 数据库 |
| [reports/library-footprints.csv](reports/library-footprints.csv) | 当前全部 117 项可放置封装 |
| [reports/personal-symbols.csv](reports/personal-symbols.csv) | 61 个符号及候选封装、未匹配项 |
| [reports/personal-issues.csv](reports/personal-issues.csv) | 本次待核对项 |
| [reports/library-models.csv](reports/library-models.csv) | 当前活动模型的文件大小与 SHA256 |
| [reports/personal-models.csv](reports/personal-models.csv) | 本次输入到库目录的逐文件对应与 SHA256 |
| `sources/` | 已有开源模型的许可、BOM 和导出资料 |

## 检查与维护

```bash
python3 scripts/validate_library.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Windows 将 `python3` 换成 `python`。原始输入仍在库外时可重现本次导入：

```bash
python3 scripts/import_personal.py --olb ../LIB_COMMON.OLB --fpx ../FPX
```

脚本拒绝覆盖内容不同的已有文件，也拒绝替换已被手工编辑的个人生成记录。已有基础库导入脚本必须使用独立暂存目录 `--root`，不能直接重生成本次整合后的库。生成脚本中的原始 Windows 路径已保留，重新生成封装前应在本机检查并调整；本次未执行这些脚本。

- [导入结果及限制](reports/README.md)
- [Cadence 路径配置](docs/cadence-24.1-setup.md)
- [完成一个器件](docs/quickstart.md)
- [器件清单字段](docs/catalog-schema.md)
- [来源和许可](sources/README.md)
- [GitHub SSH](docs/github-ssh.md)

完全离线使用无需 GitHub 或云端 Workspace。Git 仓库及 SSH 配置已保留。
