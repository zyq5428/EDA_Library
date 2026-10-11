# 原理图符号库

`LIB_COMMON.OLB` 是用户创建的原始库，完整复制，共读取到 61 个 Packages 条目；没有修改库内属性或引脚。

在 Capture 中通过 `Place → Part → Add Library` 添加本文件。`../reports/personal-symbols.csv` 提供符号名称和封装候选，候选仅来自内部同名文本，不能证明 PCB Footprint 属性和引脚映射已验证。47 项有唯一候选，13 项未匹配，1 项涉及 SOT23-5 冲突。

核对符号的 `PCB Footprint`，使用 `../reports/library-footprints.csv` 的名称。随后在独立项目生成网表、导入 PCB 并逐脚核对连接。
