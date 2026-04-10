# 杂粮育种信息抽取：实体与关系分类学体系 (K8)

本文档基于 CCL 2026 MGBIE 任务的官方标注说明，结合高引用农业文献和真实评测数据，为 12 类实体和 6 类关系提供权威定义、边界规则和典型示例。

## 1. 实体分类体系 (12类)

### 1.1 核心生物学实体
| 类型 | 标签 | 权威定义与说明 | 典型示例 (来自真实数据) |
|---|---|---|---|
| **作物** | `CROP` | 杂粮作物的物种或类别名称，用于指明研究对象。通常是属名、种名或通用俗名 [1]。 | foxtail millet, Sorghum, Setaria italica, oat, barley |
| **品种** | `VAR` | 审定、登记或推广的具体品种名称、代号或地方品系 (Landrace) [2]。 | 晋谷21, BaYou 9, SC56, early-maturing varieties, Jitian 3 |
| **亲本/杂交组合** | `CROSS` | 用于构建作图群体或育种的父本/母本材料，及其杂交组合或衍生群体（如 RIL, F2, DH）[3]。 | F-2 population, F-1 hybrids, parent lines, RIL populations |

### 1.2 遗传与基因组实体
| 类型 | 标签 | 权威定义与说明 | 典型示例 (来自真实数据) |
|---|---|---|---|
| **基因** | `GENE` | 与性状相关的功能基因、候选基因名称或基因家族。必须包含完整的字母和数字编号 [4]。 | ABA Insensitive 5 (ABI5), Hsf10, Waxy, ribosome, FtbHLH2 |
| **数量性状位点** | `QTL` | 与数量性状相关的遗传位点或染色体区间标识。通常以 `q` 开头 [5]。 | QTLs, metaQTL (MQTL), QTL regions, qBX7.1, drought tolerance QTL |
| **分子标记** | `MRK` | 用于定位或选择的 DNA 序列多态性标记（如 SSR, SNP, InDel, KASP）[6]。 | SSR markers, SNPs, DArT, primer pairs, InDels |
| **染色体** | `CHR` | 染色体编号、名称或特定的染色体区域 [5]。 | chromosomes, 6H, chromosome 2H, SBI-10, chromosomal regions |

### 1.3 表型与环境实体
| 类型 | 标签 | 权威定义与说明 | 典型示例 (来自真实数据) |
|---|---|---|---|
| **性状** | `TRT` | 表型、农艺、品质或抗性等特征名称。不包含具体的数值或高低状态 [7]。 | flowering time, grain length, panicle weight (PW), drought-resistant |
| **生育时期** | `GST` | 作物生长发育的特定阶段节点 [8]。 | heading stage, maturity, germination stage, flowering, booting stage |
| **非生物胁迫** | `ABS` | 由非生命环境因素（如干旱、盐碱、极端温度）引起的胁迫条件 [9]。 | salt stress, cold stresses, simulated drought, saline-alkali stress |
| **生物胁迫** | `BIS` | 由病原体、害虫或杂草等生物因素引起的胁迫类型 [10]。 | aphid, blast, crown rust, Puccinia striiformis, E. graminis |

### 1.4 方法学实体
| 类型 | 标签 | 权威定义与说明 | 典型示例 (来自真实数据) |
|---|---|---|---|
| **育种方法** | `BM` | 育种、选择或遗传分析的技术路线与方法（如 GWAS, RNA-seq, MAS）[11]。 | genome-wide association study, RNA-seq, Marker-assisted breeding |

---

## 2. 关系分类体系 (6类)

### 2.1 属性与归属关系
| 关系名称 | 标签 | 允许的头尾实体类型 | 权威定义与说明 | 典型示例 |
|---|---|---|---|---|
| **包含** | `CON` | `CROP` -> `VAR` <br> `CROSS` -> `VAR` | 品种属于某作物，或杂交组合衍生出某品种/群体。 | 「foxtail millet」(`CROP`) -> 「QTL regions」(`QTL`) (注：数据集中存在此类扩展用法) |
| **具有** | `HAS` | `VAR` -> `TRT` <br> `CROP` -> `TRT` | 品种或作物具备、表现出或被评估了某种性状 [7]。 | 「sweet sorghum」(`CROP`) -> 「flowering time」(`TRT`) |

### 2.2 遗传与定位关系
| 关系名称 | 标签 | 允许的头尾实体类型 | 权威定义与说明 | 典型示例 |
|---|---|---|---|---|
| **定位于** | `LOI` | `MRK` -> `CHR` <br> `QTL` -> `CHR` <br> `GENE` -> `CHR` | 分子标记、QTL 或基因被映射到特定的染色体或物理区间 [5]。 | 「SNPs」(`MRK`) -> 「QTL regions」(`QTL`) |

### 2.3 因果与影响关系
| 关系名称 | 标签 | 允许的头尾实体类型 | 权威定义与说明 | 典型示例 |
|---|---|---|---|---|
| **影响** | `AFF` | `ABS`/`BIS` -> `TRT` <br> `GENE`/`QTL` -> `TRT` | 胁迫条件、基因或 QTL 对性状表现产生直接影响或调控作用 [9]。 | 「E. graminis」(`BIS`) -> 「powdery mildew resistance」(`TRT`) |

### 2.4 时空与方法关系
| 关系名称 | 标签 | 允许的头尾实体类型 | 权威定义与说明 | 典型示例 |
|---|---|---|---|---|
| **发生于** | `OCI` | `TRT`/`ABS`/`BIS` -> `GST` | 性状的测定、胁迫的施加或病害的发生处于特定的生育时期 [8]。 | 「severe stress」(`ABS`) -> 「booting stage」(`GST`) |
| **采用** | `USE` | `VAR` -> `BM` <br> `CROP` -> `BM` | 品种选育或作物研究中使用了特定的技术方法 [11]。 | 「sweet sorghum」(`CROP`) -> 「Marker-assisted breeding」(`BM`) |

## 参考文献
[1] U.S. Department of Agriculture. (2020). Sorghum Production Statistics.
[2] NY/T 2425-2013. 植物新品种特异性、一致性和稳定性测试指南 谷子.
[3] Kumar, N., et al. (2023). Development and characterization of a sorghum multi-parent advanced generation inter-cross (MAGIC) population. G3 Genes|Genomes|Genetics.
[4] CGSNL. (2008). Gene Nomenclature System for Rice. Rice.
[5] Jellen, E. N., et al. (2024). A uniform gene and chromosome nomenclature system for oat (Avena spp.). Crop & Pasture Science.
[6] Baloch, F. S., et al. (2023). Recent advancements in the breeding of sorghum crop: current status and future strategies for marker-assisted breeding. Frontiers in Genetics.
[7] NY/T 2355-2013. 植物新品种特异性、一致性和稳定性测试指南 燕麦.
[8] Bayer Crop Science. (2021). Sorghum Growth Stages.
[9] Wu, C., et al. (2023). Salt stress responses in foxtail millet: Physiological and molecular mechanisms. Plant Science.
[10] Negi, et al. Decoding the resistance in millets towards biotic stress. Journal of Phytological Research.
[11] Yabe, S., et al. (2020). Genomics-assisted breeding in minor and pseudo-cereals. Molecular Breeding.
