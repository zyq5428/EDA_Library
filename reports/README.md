# 当前整合结果

当前活动库包含 1 个 OLB（61 个符号）、117 个 PSM、155 个 DRA、447 个 PAD、31 个 SSM、12 个 FSM 和 42 个 STEP/STP，共 805 个活动模型文件；清单共 246 条 draft。

- `library-models.csv` / `library-footprints.csv`：当前全库哈希与封装索引。
- `personal-models.csv`：本次逐文件来源与目标对应，包含备用封装及工程文件。
- `personal-symbols.csv`：61 项符号及 47 项候选匹配；13 项未匹配，1 项 SOT23-5 冲突。
- `personal-footprints.csv`：FPX 的 42 项 PSM，其中 41 项在活动目录，1 项隔离。
- `personal-issues.csv` / `conflicts.csv`：未匹配、缺失源图/脚本引用及同名冲突。
- `personal-parts.generated.csv`：新增 103 条记录的生成快照。

FPX 有 5 个 PSM 未提供同名 DRA，保留 PSM，未伪造源图。部分生成脚本引用的 PAD 或 STEP 未在输入中提供，相关字段只登记确实存在的文件。3D 候选来自脚本的精确名称，未按相似名称替代；未验证原生封装中的实际映射、单位或旋转。

OLB 只读取 Packages 名称和内部 ASCII 文本来整理候选，没有改写属性。所有新增记录为 draft；仍需 Windows Cadence 放置、网表、引脚与几何检查。

# 基础库导入记录

本页以下表格记录个人库整合前的基础库导入快照，数量不是当前全库总数。模型目录保持扁平。原始输入 `BeagleBadgeLib` 与 `BeagleBadge` 未修改；旧的项目分目录、精简分支、数据库候选表和专用导入脚本已清理。

| 项目 | 数量 | 说明 |
| --- | ---: | --- |
| 物理文件 | 651 | 118 DRA、76 PSM、415 PAD、30 SSM、12 FSM |
| 可放置封装 | 76 | 均有同名 DRA |
| 封装索引 | 76 | 包含已补齐 PSM 的 r0805 |
| 器件导出文本 | 161 | devices.map 仅列部分名称，不按它单独计数 |
| 去重文本器件 | 142 | 按符号候选、封装、Value 合并重复 DISCRETE 导出 |
| 草稿清单 | 143 | 142 条文本器件及 1 条新增 r0805 记录 |
| 引脚文本映射 | 1574 | PINORDER / FUNCTION 长度及 PINCOUNT 一致性通过 |
| 原始 BOM 条目 | 150 | 排除文件尾部空白 form-feed 行 |

## 报告用途

- `footprints.csv`：封装文件、状态、关联草稿编号。
- `models.csv`：651 个文件的 SHA256、大小、类型及来源。
- `devices.csv` / `pins.csv`：器件文本和逐单元物理引脚映射。
- `bom.normalized.csv`：原始采购 BOM 的范围与位号。
- `bom-matches.csv`：只有导出 Value 与主板 BOM 的 MPN 相等时提供候选关联；不根据近似名称强行猜型号。
- `parts.generated.csv`：本次器件清单生成快照；日常维护入口是根目录 parts.csv。
- `issues.csv`：缺失文件、符号库及待核对事项。

## BOM 层级处理

源 BOM 的 `2.1` 是板上的无线模块，`2.1.1…2.1.16` 是该模块内部 BOM，不能按其 U1、C1 等位号与主板器件混合。本次记录 130 条主板 BOM、16 条子装配 BOM、1 条 `.D` 替代料及 3 条非 PCB/装配项。替代料不是 DNP；未按表内重复位号制造冲突，也未把子装配器件错误分配到主板封装。

## 尚待完成

1. r0805 的 DRA、PSM 和用户确认的 PAD 已关联，文件缺失项已清除；仍需在 PCB Editor 中核对实际引用、尺寸和引脚。
2. 基础库输入没有 OLB：符号名仅是 PCB 器件文本提供的候选；Symbol_Library 留空。原理图 PDF 不能直接当作 Capture 库导入。
3. 所有 PAD 全量保留，具体封装依赖尚未解析。用户已确认 r0805 复用 `1_016x1_397mm_rec.pad`，该项已登记到 Padstack_Paths；其余未确认依赖仍留空。此声明尚未在原生 DRA 中独立核对。
4. 尺寸、阻焊、钢网、原点、引脚 1 及数据手册对应关系尚未验证。
5. 普通阻容的导出 Value 是阻值/容值，不是采购型号，故 MPN 没有被自动当成 Value 填入。采购信息不完整的记录保留草稿。
6. r0805 属用户补充文件，来源和许可尚未提供；不能据其名称自动套用开源板许可。

导出日志显示 0 项 ERROR，记录在 sources/export-logs；这不代表库已完成几何与电气验证。完成检查后逐条升级状态。
