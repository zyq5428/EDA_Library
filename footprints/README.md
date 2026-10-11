# PCB 封装与辅助符号

本目录采用扁平布局，已有 76 对 DRA / PSM、30 对 DRA / SSM、12 对 DRA / FSM；其中 `r0805.dra` 和用户补充的 `r0805.psm` 已配套，复用 `1_016x1_397mm_rec.pad`。

封装清单见 `../reports/footprints.csv`；全部物理文件哈希见 `../reports/models.csv`。SSM / FSM 是辅助符号，不应作为额外器件封装统计。

将 psmpath 指向本目录，padpath 指向 `../padstacks`。保留原文件名及内部引用；如要改名，应在 Cadence 中更新引用并重新生成编译符号。

本次只整理模型，未验证尺寸、孔径、钢网或逐封装 PAD 依赖。可放置不等于已审核。
