# 大跃进计划数据底稿（自动统计）

## 1. 关键提交版本总体统计

| 版本 | 已知分数 | 关系数 | 关系均值 | 无关系样本 | 实体均值 | Top关系类型 |
| :--- | ---: | ---: | ---: | :--- | ---: | :--- |
| `submit_v36_gene_abs` | 0.4487 | 1081 | 2.70 | 111 (27.8%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:159, QTL-LOI-TRT:123, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v41_sub_conservative` | 0.4510 | 1056 | 2.64 | 112 (28.0%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v44_del_var_con_cross` | 0.4514 | 1052 | 2.63 | 112 (28.0%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v45_del_gene_loi_mrk` |  | 1047 | 2.62 | 112 (28.0%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v45_fix_gene_mrk_direction` |  | 1052 | 2.63 | 112 (28.0%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v45_del_low_freq_types` |  | 1039 | 2.60 | 113 (28.2%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v45_del_all_risks` |  | 1034 | 2.58 | 113 (28.2%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v45_fix_cross_con_var` |  | 1056 | 2.64 | 112 (28.0%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v45_fix_cross_del_gene_mrk` |  | 1051 | 2.63 | 112 (28.0%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |
| `submit_v45_fix_both_directions` |  | 1056 | 2.64 | 112 (28.0%) | 7.18 | ABS-AFF-TRT:163, VAR-HAS-TRT:158, QTL-LOI-TRT:117, GENE-AFF-TRT:86, ABS-AFF-GENE:71, CROP-CON-VAR:69 |

## 2. v44底座中的低频关系库存（训练集频次<=5）

| 类型 | v44数量 | 训练集频次 |
| :--- | ---: | ---: |
| GENE-CON-TRT | 4 | 1 |
| QTL-AFF-BIS | 3 | 1 |
| VAR-OCI-GST | 2 | 1 |
| BM-USE-CROSS | 1 | 1 |
| GENE-LOI-MRK | 5 | 2 |
| BM-AFF-GENE | 2 | 2 |
| BIS-CON-BIS | 1 | 2 |
| BM-USE-QTL | 1 | 2 |
| GENE-LOI-CROP | 1 | 2 |
| CROSS-USE-BM | 1 | 3 |
| CROSS-USE-MRK | 1 | 3 |
| MRK-USE-BM | 1 | 3 |
| TRT-AFF-GENE | 1 | 3 |
| BM-USE-TRT | 3 | 4 |
| QTL-CON-QTL | 1 | 4 |
| VAR-CON-GENE | 1 | 4 |
| BIS-AFF-BIS | 3 | 5 |
| TRT-LOI-CHR | 3 | 5 |
| GENE-OCI-GST | 1 | 5 |
| QTL-CON-GENE | 1 | 5 |

## 3. v45候选相对v44底座的差异

| 候选 | 删除数 | 新增数 | 删除类型Top | 新增类型Top |
| :--- | ---: | ---: | :--- | :--- |
| `submit_v45_del_gene_loi_mrk` | 5 | 0 | GENE-LOI-MRK:5 |  |
| `submit_v45_fix_gene_mrk_direction` | 5 | 5 | GENE-LOI-MRK:5 | MRK-LOI-GENE:5 |
| `submit_v45_del_low_freq_types` | 13 | 0 | GENE-CON-TRT:4, QTL-AFF-BIS:3, VAR-OCI-GST:2, BM-AFF-GENE:2, GENE-LOI-CROP:1, BIS-CON-BIS:1 |  |
| `submit_v45_del_all_risks` | 18 | 0 | GENE-LOI-MRK:5, GENE-CON-TRT:4, QTL-AFF-BIS:3, VAR-OCI-GST:2, BM-AFF-GENE:2, GENE-LOI-CROP:1, BIS-CON-BIS:1 |  |
| `submit_v45_fix_cross_con_var` | 0 | 4 |  | CROSS-CON-VAR:4 |
| `submit_v45_fix_cross_del_gene_mrk` | 5 | 4 | GENE-LOI-MRK:5 | CROSS-CON-VAR:4 |
| `submit_v45_fix_both_directions` | 5 | 9 | GENE-LOI-MRK:5 | MRK-LOI-GENE:5, CROSS-CON-VAR:4 |

## 4. 方向与低频关系样例

### GENE-LOI-MRK
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 13 | lgs gene | LOI | microsatellite markers SB3344 | Using a linkage map with 367 markers (DArT and SSRs) and an in vitro assay for germination stimulant activity towards Striga asiatica in 354 recombinant inbred lines from SRN39 (low stimulant) x Shanqui Red (high stimula |
| 13 | lgs gene | LOI | SB3352 | Using a linkage map with 367 markers (DArT and SSRs) and an in vitro assay for germination stimulant activity towards Striga asiatica in 354 recombinant inbred lines from SRN39 (low stimulant) x Shanqui Red (high stimula |
| 103 | HORVU7Hr1G000320 | LOI | SNP7 | Two candidate genes, HORVU7Hr1G000320 and HORVU7Hr1G000040, are linked to SNP7. They belong to the nucleotide triphosphate hydrolase superfamily and may affect beta-glucan synthase activity. Another candidate gene, HORVU |
| 103 | HORVU7Hr1G000040 | LOI | SNP7 | Two candidate genes, HORVU7Hr1G000320 and HORVU7Hr1G000040, are linked to SNP7. They belong to the nucleotide triphosphate hydrolase superfamily and may affect beta-glucan synthase activity. Another candidate gene, HORVU |
| 103 | HORVU1Hr1G000010 | LOI | SNP1 | Two candidate genes, HORVU7Hr1G000320 and HORVU7Hr1G000040, are linked to SNP7. They belong to the nucleotide triphosphate hydrolase superfamily and may affect beta-glucan synthase activity. Another candidate gene, HORVU |

### GENE-CON-TRT
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 372 | AsTCP genes | CON | hormone response | The promoters of AsTCP genes contain cis-acting elements for hormone response, abiotic stress, light response, and growth and development. The oat TCP gene family is mainly amplified by fragment duplication. Two tandem d |
| 372 | AsTCP genes | CON | abiotic stress | The promoters of AsTCP genes contain cis-acting elements for hormone response, abiotic stress, light response, and growth and development. The oat TCP gene family is mainly amplified by fragment duplication. Two tandem d |
| 372 | AsTCP genes | CON | light response | The promoters of AsTCP genes contain cis-acting elements for hormone response, abiotic stress, light response, and growth and development. The oat TCP gene family is mainly amplified by fragment duplication. Two tandem d |
| 372 | AsTCP genes | CON | growth and development | The promoters of AsTCP genes contain cis-acting elements for hormone response, abiotic stress, light response, and growth and development. The oat TCP gene family is mainly amplified by fragment duplication. Two tandem d |

### QTL-AFF-BIS
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 50 | Resistance loci | AFF | pathotypes from Texas and Puerto Rico | Resistance loci against pathotypes from Texas and Puerto Rico are flanked by SSR markers Ch5-55.0 and Ch5-56.1. The resistance locus against pathotypes from Arkansas is 9.5 cM below SSR marker Ch5-56.1. The resistance lo |
| 50 | resistance locus | AFF | pathotypes from Arkansas | Resistance loci against pathotypes from Texas and Puerto Rico are flanked by SSR markers Ch5-55.0 and Ch5-56.1. The resistance locus against pathotypes from Arkansas is 9.5 cM below SSR marker Ch5-56.1. The resistance lo |
| 50 | resistance locus | AFF | pathotypes from Georgia | Resistance loci against pathotypes from Texas and Puerto Rico are flanked by SSR markers Ch5-55.0 and Ch5-56.1. The resistance locus against pathotypes from Arkansas is 9.5 cM below SSR marker Ch5-56.1. The resistance lo |

### BM-USE-TRT
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 269 | Integrative breeding | USE | early maturity | Sorghum grain yield is low in arid and semi-arid regions due to a lack of improved varieties tolerant to drought, heat, and biotic constraints. Integrative breeding for early maturity, high harvest index, and water use e |
| 269 | Integrative breeding | USE | high harvest index | Sorghum grain yield is low in arid and semi-arid regions due to a lack of improved varieties tolerant to drought, heat, and biotic constraints. Integrative breeding for early maturity, high harvest index, and water use e |
| 269 | Integrative breeding | USE | water use efficiency | Sorghum grain yield is low in arid and semi-arid regions due to a lack of improved varieties tolerant to drought, heat, and biotic constraints. Integrative breeding for early maturity, high harvest index, and water use e |

### VAR-OCI-GST
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 80 | Baiyan 2 | OCI | three-leaf stage | The oat cultivar Baiyan 2 at the three-leaf stage was used to investigate drought resistance. Seedlings were treated with polyethylene glycol (PEG) to simulate drought stress. Photosynthetic parameters and physicochemica |
| 399 | BTx623 | OCI | seed development | The inbred line 'BTx623' of sorghum was analyzed for spatiotemporal transcriptome and metabolome profiles during seed development. Morphological and molecular analyses identified key seed maturation stages. Starch biosyn |

### BM-AFF-GENE
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 177 | CRISPR/Cas9 | AFF | susceptibility genes | CRISPR/Cas9 targeted modification of susceptibility genes in rice, tomato, wheat, and citrus is reviewed for resistance to fungal and bacterial diseases. This genome editing develops crop plants resistant to specific pes |
| 209 | MAT | AFF | phytoene desaturase gene | The MAT approach edited the phytoene desaturase gene. A high-throughput technique and a novel method were developed to identify single-copy transformed plants and determine transgene independent integration. |

### CROSS-USE-MRK
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 49 | F-2 population | USE | RAD-seq | A cross between Aininghuang and Jingu 21 produced an F-2 population of 543 foxtail millet plants. A high-density linkage map was constructed using RAD-seq. QTLs for 11 agronomic traits (PH, PL, PD, PNL, FID, SID, PW, GW, |

### VAR-CON-GENE
| idx | head | label | tail | text片段 |
| ---: | :--- | :--- | :--- | :--- |
| 64 | sdw1.ZU9 | CON | HvGA20ox2 | A novel allele sdw1.ZU9 contains a 96-bp fragment in the promoter region of HvGA20ox2. This fragment is associated with lower gene expression, leading to lower plant height but higher germination rate. It was primarily o |

