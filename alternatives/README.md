# 同名备用封装

`sot23-5/` 保存 FPX 的原始 DRA/PSM；它们与活动库已有同名文件内容不同，因此未覆盖。

如需纳入共享库，在 Cadence 中打开备用 DRA，另存唯一包名并生成对应 PSM，再更新 OLB 的 PCB Footprint 及清单。不要仅在文件系统中重命名，也不要同时加载两个同名搜索目录。冲突文件哈希见 reports/personal-models.csv。
