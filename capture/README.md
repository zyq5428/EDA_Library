# 原理图符号库

使用 Capture 新建或维护真实 `.olb` 文件，建议初期使用 `Passives.olb`、`Power.olb`、`MCU.olb`、`Interfaces.olb`、`Connectors.olb`、`Mechanical.olb`。

这里没有占位 `.olb` 文件。在 Capture 中通过 `Place → Part → Add Library` 添加真实库。Component Explorer 的器件记录应关联其中的实际符号。

每个符号检查引脚名称、编号、电气类型、隐藏电源脚与多单元设置。符号编号必须匹配目标封装编号；仅引脚数量相同不代表可互换。
