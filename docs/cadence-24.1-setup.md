# Cadence 24.1 本地配置

本说明适用于 OrCAD X Capture CIS 和传统 PCB Editor。模型放在固定的个人目录，如 `D:/EDA_Library`，不放入 Cadence 安装目录。

## PCB Editor

打开 `Setup → User Preferences → Paths → Library`，添加以下路径，不覆盖已有路径：

| 设置 | 路径 |
| --- | --- |
| psmpath | D:/EDA_Library/footprints |
| padpath | D:/EDA_Library/padstacks |
| steppath | D:/EDA_Library/step |

所有物理模型采用扁平目录，不需要添加项目子目录。避免其他搜索路径中出现同名却不同内容的模型；实际采用哪份模型取决于搜索路径顺序。

## Capture

通过 `Place → Part → Add Library` 添加 `D:/EDA_Library/capture/LIB_COMMON.OLB`。该文件保留用户原始内容，共 61 个符号。

在符号的 Package Properties 中设置 `PCB Footprint`，使用 `reports/library-footprints.csv` 中的名称，如 `r0402`、`r0603`，不含目录和扩展名。r0805 的 DRA / PSM 已配套，可使用名称 `r0805`。

`reports/devices.csv` 的 Symbol 列为源设计候选名；`reports/pins.csv` 可用于对照物理引脚号，但不是 OLB 的引脚解析结果。一个符号可对应多个封装，使用普通 OLB 时可按封装建立变体；使用 CIS 时可在数据库中分别登记具体器件。

## 完整器件和数据库

`parts.csv` 是离线索引，不自动同步到 Component Explorer，也不是 `.dbc`。若使用 CIS ODBC，需要自行建立与 Capture 进程位数匹配的本地数据库驱动和字段映射。此步骤不影响直接加载本地 OLB 和 PCB 封装。

完成原理图到 PCB 的网表和放置检查后，填写检查记录，并逐条将 draft 改为 reviewed。新库当前尚未完成这些验证。

本次候选关联见 `reports/personal-symbols.csv`，未自动写回 OLB。FPX 同名不同内容的 SOT23-5 在 `alternatives/sot23-5/`，默认不加载；如需使用，先在 Cadence 中另存唯一名称并生成 PSM。STEP 路径已配置仍需确认封装内 3D 映射及坐标，不能仅凭同名认定已关联。
