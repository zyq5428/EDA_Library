# 模型来源与许可

官方源仓库：[BeagleBadge](https://github.com/beagleboard/BeagleBadge)，本次本地提交 `913d7402e97a5b6f7b6fb2332bcc9b7b52c6a5e1`。原始 PCB 为 `design/BeagleBadge_V1.0_260826.brd`，本次导出日志中的板文件名与之对应。

Copyright (c) 2026 SEEED Technology Co., Ltd.；Copyright (c) 2026 Jason Kridner, BeagleBoard.org Foundation。硬件设计许可为 **CC-BY-SA-4.0**，实际源仓库 `design/LICENSE` 全文保存在 [LICENSE](LICENSE)。源仓库文档的 MIT 许可不用于这些硬件设计。

本次复制已有模型，保留原始名称和字节；新增扁平组织、哈希索引、器件草稿、BOM 层级标记和引脚文本报告。它是个人整理库，不是 Cadence 官方器件库。

用户增加的 r0805 不是导出日志中的模型，其来源与许可待补，已在 models.csv 单独标记，不自动归入 CC-BY-SA。

- `BOM.csv`：源仓库的原始采购 BOM，未改写。
- `devices/`、`devices.map`：原始器件导出文本和部分名称映射。
- `export-logs/`：原始导出日志，保留软件版本和检查记录。
- `provenance.json`：来源提交、许可、BOM 哈希和导入统计。

源设计与导出库仍保留在仓库外输入目录中，不在模型目录按项目来源划分子库。

## 个人新增模型

`capture/LIB_COMMON.OLB` 来自用户自建库；FPX 封装、PAD、3D、`projects/Hero.fpx` 及 `projects/exports/` 来自用户提供的 FPX 文件夹。原始字节已保留，逐文件 SHA256 见 `../reports/personal-models.csv`。不对这些文件套用开源板的 CC-BY-SA 许可，也没有推断新的公开再分发授权。

当前汇总在 `../metadata/library-summary.json`；`provenance.json` 与基础模型报告仍保留基础库导入统计，个人导入统计在 `../metadata/personal-import.json`。
