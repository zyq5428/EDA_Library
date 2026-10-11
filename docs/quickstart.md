# 第一个器件入库

建议先选择手头已有的一个具体型号，例如实际采购的电阻或电源芯片，完成全流程后再扩充。

1. **登记草稿**：从 `templates/part-record.csv` 复制草稿行到 `parts.csv`，分配唯一 `Part_ID`，修改类别和描述。模板行只是填写示例，不是实际器件。
2. **获取模型**：使用厂商资料、自建模型或开源板导出文件。第三方文件先存 `incoming/Part_ID/`，记录原始来源和许可。无论来源是否知名，都要核对。
3. **建立物理模型**：使用 Padstack Editor 核对焊盘；使用 PCB Editor 编辑 `.dra` 并生成 `.psm`。真实模型移入 `padstacks/`、`footprints/`，可选 STEP 放入 `step/`。
4. **建立符号**：在 Capture 库中创建或整理符号，保存真实 `.olb` 到 `capture/`。IC 与连接器必须按目标型号核对引脚名称、编号、方向。
5. **关联完整器件**：在 Component Explorer 中创建或编辑器件，分类并关联符号和封装；登记个人料号、Manufacturer、完整 MPN、参数、datasheet。
6. **实用验证**：在独立小项目放置器件，生成网表并导入 PCB；确认封装正确、没有缺失焊盘，逐脚核对电气连接。对连接器或异形器件可做 1:1 打印比对；需要 3D 时核对原点和高度。
7. **填写检查记录**：复制 `templates/component-review.md` 到 `docs/components/Part_ID.md`，记录实际结果。完善 CSV 的文件路径与版本，状态改为 `reviewed`。实板确认后才改为 `board_tested`。
8. **检查和提交**：运行 `python scripts/validate_library.py`。检查暂存内容，提交模型与记录；可选发布到自己的 Cloud Workspace 并回填修订号。

优先积累 0402/0603/0805 阻容、常用排针、测试点、安装孔及当前项目实际使用的电源、MCU、接口和连接器。分类统一使用 `templates/categories.csv` 的值。

## 从开源 PCB 提取

在传统 PCB Editor 中打开合法获取的 Allegro `.brd`，使用 `File → Export → Libraries` 导出封装符号与 padstacks 到 `incoming/` 的独立子目录。

先检查导出日志和文件是否完整，再逐个入库。不要直接将所有文件复制到正式库，避免同名焊盘覆盖和项目专用钢网/焊盘修改被误用。旧数据库可能需要升级；保留原文件并在副本上操作。

[Cadence 导出说明](https://community.cadence.com/cadence_technology_forums/pcb-design/f/pcb-design/11515/exporting-saving-footprints-from-brd-file)
