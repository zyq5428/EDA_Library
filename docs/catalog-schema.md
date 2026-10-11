# 器件清单字段

`parts.csv` 使用 UTF-8，英文列名，路径相对仓库根目录并使用 `/`。Excel 编辑后保存为 UTF-8 CSV；含逗号的字段需要 CSV 引号。文件只含表头时表示空库。

| 列 | 含义 |
| --- | --- |
| Part_ID | 唯一且稳定的个人器件编号 |
| Category | templates/categories.csv 中的类别 |
| Manufacturer | 厂商；纯机械自建件可填 SELF |
| MPN | 完整订购型号；自建机械件可填稳定自定义型号 |
| Description | 器件说明 |
| Value | 阻值、容值等，可选 |
| Parameters | 额定电压、功率、精度等，可选 |
| Symbol_Library | 如 capture/Passives.olb |
| Symbol_Name | .olb 内真实符号名，脚本不能解析验证 |
| PCB_Footprint | 封装名称，不带扩展名 |
| Footprint_DRA | 如 footprints/MY_R_0603_R01.dra |
| Footprint_PSM | 同名 .psm 相对路径 |
| Padstack_Paths | 所有依赖 .pad 路径，以分号分隔 |
| STEP_Path | 可选 STEP 相对路径 |
| Datasheet_URL | 目标器件尺寸/引脚依据，可选于自建件 |
| Source_URL | 模型或设计原始来源链接 |
| License_Notes | 来源许可、原创或仅本地使用的说明 |
| Revision | 本仓库器件修订，例如 R01 |
| Status | draft / reviewed / board_tested / deprecated |
| Review_Path | docs/components/Part_ID.md |
| Workspace_Revision | 可选的云端器件修订号 |
| Notes | 其他说明 |

## 状态

- `draft`：待检查，允许模型和采购信息未完成；至少填写 Part_ID、Category、Description、Status。
- `reviewed`：完成检查并验证原理图到 PCB 流程。
- `board_tested`：在具体实板中确认，记录项目和日期。
- `deprecated`：保留给历史项目，不推荐新设计使用；模型仍应可解析。

非 draft 行必须填写厂商、型号、符号库与名称、封装、焊盘依赖、许可说明、修订及检查记录，并确保引用文件存在。若特殊封装没有 padstack（例如纯机械轮廓），Padstack_Paths 填 `NONE` 并在检查记录中说明。

需要目录扩展时同步修改分类模板。脚本不会证明 `reviewed` / `board_tested` 状态真实，也不会检查外部 URL 可达性、datasheet 许可或库内电气内容。

## CIS 与 Workspace

本清单不替代 CIS ODBC 数据库。迁移时将各列映射至数据库字段，并按本机部署映射符号库和物理模型路径，避免把不同机器的绝对路径写回 Git 索引。

新建或修改 Workspace 器件后，同步维护本清单；发布云端后填写 Workspace_Revision，关联两边的版本。
