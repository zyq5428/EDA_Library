# Cadence 24.1 配置

本说明以 OrCAD X Capture CIS + 传统 Allegro PCB Editor 24.1 为主。System Capture、Presto 的界面与库管理方式不同，不直接照搬 PCB Editor 菜单。

## 本地目录

将仓库克隆到固定位置，例如 `D:/EDA_Library`。不要放进 `C:/Cadence/SPB_24.1` 安装目录，也不要直接把 Git 仓库设为 Cadence 自动管理的 Workspace 内部目录。

在 PCB Editor 中打开：

```text
Setup → User Preferences → Paths → Library
```

添加以下路径（按实际克隆位置调整）：

| 选项 | 路径 | 内容 |
| --- | --- | --- |
| psmpath | D:/EDA_Library/footprints | .psm 封装 |
| padpath | D:/EDA_Library/padstacks | .pad 焊盘 |
| steppath | D:/EDA_Library/step | STEP 模型 |

使用对话框添加路径，不覆盖已有路径。通常将个人库放在软件默认库之前；项目冻结库应优先于个人最新库。避免同名模型冲突。子目录不会因配置父目录而自动全部加入，拆分目录时逐项配置。

通过一个真实封装验证设置：能够找到并放置封装，所有焊盘存在，STEP 能正确显示。仓库初建没有模型，暂时无法完成此验证。

## 原理图符号与器件入口

- 普通 Capture `.olb`：在 `Place → Part → Add Library` 添加本仓库 `capture/` 内的真实库。
- OrCAD X Capture CIS：通过 `Place → Component` 打开 Component Explorer，管理自己的 Workspace 器件。
- 将器件记录关联到真实原理图符号和 PCB 封装，检查 MPN、参数与引脚映射。
- 传统 Capture 的 `PCB Footprint` 属性使用封装名称，例如 `MY_SOIC8_P127_BODY390_R01`，通常不带目录和 `.psm` 扩展名。
- Component Explorer 的文件管理操作不会自动读取或同步 `parts.csv`。器件记录与仓库索引需要同步维护。

## 云端修订管理

有可用 OnCloud 服务和账户时，在 Component Explorer 中对器件使用 `Publish` 并选择自己的目标 Workspace。首次发布前确认关联文件、分类、属性和版本。

本地 Workspace 只提供本地存储，并不等于云端的版本与协作管理。Git 与 Cloud Workspace 也不自动互相同步；在检查记录中登记 `workspace_revision`。

纯离线使用时，可通过 CIS ODBC 配置自己的数据库。需建立数据库、字段及模型路径映射并生成对应 `.dbc`；本仓库 CSV 只是字段参考，不能直接作为 `.dbc` 使用。

## 参考

- [24.1 Workspace 管理](https://resources.pcb.cadence.com/orcad-x-data-management-faqs/how-to-create-and-manage-workspaces-in-orcad-x-capture-cis-241)
- [Component Explorer 发布器件](https://community.cadence.com/cadence_technology_forums/pcb-design/f/allegro-x-capture-cis/59099/sharing-a-component-in-the-shared-workspace)
- [封装子目录与搜索路径](https://community.cadence.com/cadence_technology_forums/pcb-design/f/pcb-design/24227/breaking-down-foot-print-libraries-into-categories/1316921)
