# 杂粮育种信息抽取：生僻术语词表 (K3)

本文档收集了杂粮（谷子、高粱、燕麦、荞麦等）育种文献中常见的生僻术语、拉丁学名和技术缩写，并明确其对应的实体类别，以减少分类错误。

## 1. 谷子 (Foxtail Millet) 术语

| 中文术语 | 英文/拉丁文 | 对应实体类别 | 解释说明 |
|---|---|---|---|
| 谷子 / 粟 | *Setaria italica* | `CROP` | 栽培种谷子 [1] |
| 青狗尾草 | *Setaria viridis* | `CROP` | 谷子的野生祖先种 |
| 穗码 | Panicle branch / Spikelet | `TRT` (作为部位修饰) | 谷子穗上的分枝结构，分为一级码、二级码 [1] |
| 猫耳叶 | Cat-ear leaf | `TRT` | 谷子特有的叶片形态变异 |
| 刚毛 | Bristle | `TRT` (作为部位修饰) | 谷子小穗基部的刺状附属物 [1] |
| 护颖 | Glume | `TRT` (作为部位修饰) | 包被小穗的苞片 [1] |
| 颖果 | Caryopsis | `TRT` (作为部位修饰) | 谷子的果实类型 [1] |
| 出谷率 | Grain yield rate | `TRT` | 谷穗脱粒后，籽粒重量占整个谷穗重量的百分比 [1] |
| 谷锈病 | Foxtail millet rust / *Uromyces setariae-italicae* | `BIS` | 由真菌引起的常见病害 |
| 谷瘟病 | Blast / *Magnaporthe grisea* | `BIS` | 常见真菌病害 |
| 白发病 | Smut / *Sclerospora graminicola* | `BIS` | 常见真菌病害 |
| 粳性 / 糯性 | Non-waxy / Waxy | `TRT` | 胚乳淀粉特性，由 Waxy 基因控制 |

## 2. 高粱 (Sorghum) 术语

| 中文术语 | 英文/拉丁文 | 对应实体类别 | 解释说明 |
|---|---|---|---|
| 高粱 | *Sorghum bicolor* | `CROP` | 栽培种高粱 [2] |
| 甜高粱 | Sweet sorghum | `CROP` | 茎秆富含糖分的高粱类型 |
| 丝黑穗病 | Head smut / *Sporisorium reilianum* | `BIS` | 高粱主要病害 |
| 靶斑病 | Target leaf spot / *Bipolaris sorghicola* | `BIS` | 高粱叶部病害 |
| 穗下节 | Peduncle | `TRT` (作为部位修饰) | 穗部下方的茎节，常观测其长度或茸毛 [2] |
| 护颖 | Glume | `TRT` (作为部位修饰) | 包裹小穗的苞片 |
| 锤度 / 糖度 | Brix | `TRT` | 衡量甜高粱茎秆糖分含量的指标 |

## 3. 燕麦 (Oat) 术语

| 中文术语 | 英文/拉丁文 | 对应实体类别 | 解释说明 |
|---|---|---|---|
| 燕麦 (皮燕麦) | *Avena sativa* | `CROP` | 籽粒带稃壳的燕麦 [3] |
| 裸燕麦 (莜麦) | *Avena nuda* | `CROP` | 籽粒裸露的燕麦 [3] |
| 冠锈病 | Crown rust / *Puccinia coronata* | `BIS` | 燕麦最严重的真菌病害 |
| 秆锈病 | Stem rust / *Puccinia graminis* | `BIS` | 燕麦主要病害 |
| 皮裸性 | Hullessness / Nakedness | `TRT` | 籽粒是否带壳的性状 |
| 外稃 / 内稃 | Lemma / Palea | `TRT` (作为部位修饰) | 包裹燕麦籽粒的颖壳结构 [3] |
| 旗叶 | Flag leaf | `TRT` (作为部位修饰) | 禾本科植物主茎最顶端的一片叶子 [3] |
| 穗分枝姿态 | Panicle branch attitude | `TRT` | 燕麦圆锥花序分枝的着生状态 [3] |

## 4. 荞麦 (Buckwheat) 术语

| 中文术语 | 英文/拉丁文 | 对应实体类别 | 解释说明 |
|---|---|---|---|
| 甜荞 | *Fagopyrum esculentum* | `CROP` | 异花授粉的荞麦类型 |
| 苦荞 | *Fagopyrum tataricum* | `CROP` | 自花授粉的荞麦类型 |
| 瘦果 | Achene | `TRT` (作为部位修饰) | 荞麦的果实类型 |
| 芦丁 | Rutin | `TRT` | 苦荞中富含的黄酮类化合物，核心品质性状 |
| 花柱异长 | Heterostyly | `TRT` | 甜荞具有长花柱和短花柱两种花型 |

## 5. 实验技术与群体术语 (易混淆为 BM 或 VAR)

| 术语缩写 | 全称 | 对应实体类别 | 解释说明 |
|---|---|---|---|
| RIL | Recombinant Inbred Line | `CROSS` | 重组自交系，作图群体，不是品种 |
| NIL | Near-Isogenic Line | `CROSS` | 近等基因系，作图群体 |
| DH | Doubled Haploid | `CROSS` | 双单倍体群体 |
| MAGIC | Multi-parent Advanced Generation Inter-Cross | `CROSS` | 多亲本高级世代互交群体 |
| GWAS | Genome-Wide Association Study | `BM` | 全基因组关联分析 |
| QTL mapping | Quantitative Trait Locus mapping | `BM` | QTL定位分析 |
| MAS / MAB | Marker-Assisted Selection / Breeding | `BM` | 标记辅助选择/育种 |
| RNA-seq | RNA sequencing | `BM` | 转录组测序分析 |
| ddRAD-seq | Double digest restriction-site associated DNA sequencing | `BM` | 简化基因组测序技术 |
| EMS | Ethyl methanesulfonate | `BM` | 化学诱变剂，用于创制突变体群体 |
| CRISPR/Cas9 | Clustered Regularly Interspaced Short Palindromic Repeats | `BM` | 基因编辑技术 |

## 参考文献
[1] NY/T 2425-2013. 植物新品种特异性、一致性和稳定性测试指南 谷子.
[2] NY/T 2492-2013. 植物新品种特异性、一致性和稳定性测试指南 高粱.
[3] NY/T 2355-2013. 植物新品种特异性、一致性和稳定性测试指南 燕麦.
