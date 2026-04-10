# 杂粮育种信息抽取：文献语料库 (K6)

本文档基于 CCL 2026 MGBIE 任务的真实训练数据（`train.json`），为 12 类实体和 6 类关系提供高质量的 Few-shot 标注示例。所有示例均采用官方标签体系，供模型在遇到分类困难时进行模式对标。

## 1. 实体标注示例 (Entity Few-shot Examples)

### 1.1 作物 (CROP)

| 实体文本 | 所在上下文片段 |
|---|---|
| `foxtail millet` | A genome-wide association study analyzed 425 **[foxtail millet]** samples from Xinjiang Academy using 1,304,248 SNPs. 7... |
| `barley` | ...t. Twenty-eight F-1 hybrids and eight parental lines from a **[barley]** diallel study were inoculated with five isolates of E... |
| `sweet sorghum` | ...to identify QTL associated with bioenergy-related traits in **[sweet sorghum]**, including flowering time, plant height, total biomas... |
| `sorghum` | Protoplasts were isolated from **[sorghum]** leaves. Plants were cultivated under three conditions... |
| `Sorghum` | GsNAC2 was analyzed by bioinformatics methods. **[Sorghum]** plants were treated with saline-alkali stress solutio... |
| `Quinoa` | **[Quinoa]** seedlings were treated with 24-epibrassinolide (EBR).... |
| `oat` | GWAS identified MTAs for **[oat]** nutritional quality, agronomic, and milling traits in... |
| `spring oat germplasm` | ...r oat nutritional quality, agronomic, and milling traits in **[spring oat germplasm]**. High-density sequence-based markers (15,037) were id... |
| `Arabidopsis` | FtbHLH2 localizes in the nucleus. Its overexpression in **[Arabidopsis]** increases cold tolerance. |
| `Tartary buckwheat` | ...y was artificially selected by the Wa people, who cultivate **[Tartary buckwheat]** as a staple food to prevent lysine deficiency. |
| `Setaria italica` | bZIPs are crucial for abiotic stress resistance. **[Setaria italica]** is a model for understanding stress resistance mechanisms. |
| `maize` | ...ified in this study correspond to stay green QTL regions in **[maize]**. |
| `salt-tolerant sorghum` | PUB genes play a role in regulating salt stress in sorghum. PUB genes might serve as targets for breeding **[salt-tolerant sorghum]**. |
| `Foxtail millet` | **[Foxtail millet]** is a reserve crop for extreme weather and a model cro... |
| `cowpea` | ...for seedling drought stress-induced premature senescence in **[cowpea]**. Genomic DNA from 113 F-2:8 RILs of drought-tolerant ... |
| `quinoa` | Quinoa is an economic crop. Drought affects **[quinoa]** yield. Clarifying **[quinoa]** adaptation to drought ... |
| `tobacco` | ... VfbZIP2, and VfbZIP5. Ectopic overexpression of VfbZIP5 in **[tobacco]** using a PVX vector enhanced drought tolerance. |
| `Arabidopsis thaliana` | Sorghum overcomes limitations of model species like **[Arabidopsis thaliana]**. Advances in metabolomics, transcriptomics, proteomic... |
| `grain sorghum` | ...rated from a cross between sweet sorghum cv. 'Erdurmus' and **[grain sorghum]** cv. 'Ogretmenoglu'. A genetic map was constructed fro... |
| `Sweet sorghum` | **[Sweet sorghum]** accumulates sugars in the stem parenchyma. Soluble ac... |

### 1.2 品种 (VAR)

| 实体文本 | 所在上下文片段 |
|---|---|
| `JiaYan 2` | The drought-resistant cultivar **[JiaYan 2]** (JIA2) and water-sensitive cultivar BaYou 9 (BA9) wer... |
| `JIA2` | The drought-resistant cultivar JiaYan 2 (**[JIA2]**) and water-sensitive cultivar BaYou 9 (BA9) were subj... |
| `BaYou 9` | ...stant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar **[BaYou 9]** (BA9) were subjected to three water gradient treatmen... |
| `BA9` | ...tivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (**[BA9]**) were subjected to three water gradient treatments du... |
| `RILs` | 12 QTL for leaf Delta C-13 were detected in the W x I **[RILs]**. 5 QTL were detected in the M x H **[RILs]**. For the... |
| `RIL populations` | ...length (GL), and 1 for grain width (GW) using data from 202 **[RIL populations]**. One co-located QTL for TGW was discovered on chromos... |
| `This` | ...basis of the easily dehulled trait in a particular variety. **[This]** variety was artificially selected by the Wa people, w... |
| `Jingu 21` | **[Jingu 21]** resistance to 31 herbicides was categorized into five... |
| `SC56` | The stay green line **[SC56]** is from a different source than B35. Two stay green Q... |
| `B35` | The stay green line SC56 is from a different source than **[B35]**. Two stay green QTLs identified in this study corresp... |
| `sorghum (Jitian 3)` | A GA(3) concentration of 50 mg/L is optimal for **[sorghum (Jitian 3)]** under salt stress. Whole-transcriptome analysis betwe... |
| `wild-type alleles` | ...91.01% in tiller numbers between lines with lnt2 mutant and **[wild-type alleles]**. A large F2 population was constructed and lnt2 was f... |
| `early-maturing varieties` | ...s flowering regulatory network is important for cultivating **[early-maturing varieties]**. |
| `JS6` | 833 DEGs were found in cultivar **[JS6]** and 2166 DEGs in cultivar NM5 under simulated drought... |
| `NM5` | ...3 DEGs were found in cultivar JS6 and 2166 DEGs in cultivar **[NM5]** under simulated drought using 20% PEG-6000 for 6 hour... |
| `BY` | **[BY]** utilized sugars more effectively via sugar consumptio... |
| `YZY` | ...smotic adjustment of solute concentrations and cell growth. **[YZY]** mainly used soluble sugars and flavonoids combined wi... |
| `drought-tolerant IT93K503-1` | ...re senescence in cowpea. Genomic DNA from 113 F-2:8 RILs of **[drought-tolerant IT93K503-1]** and susceptible CB46 genotypes was digested with EcoR... |
| `susceptible CB46` | ... DNA from 113 F-2:8 RILs of drought-tolerant IT93K503-1 and **[susceptible CB46]** genotypes was digested with EcoR1, HpaII, Mse1, or Ms... |
| `Bai5` | DEP in **[Bai5]** is classified into protein processing in the endoplas... |

### 1.3 亲本/杂交组合 (CROSS)

| 实体文本 | 所在上下文片段 |
|---|---|
| `F-1 hybrids` | ... and estimated each locus's resistance effect. Twenty-eight **[F-1 hybrids]** and eight parental lines from a barley diallel study ... |
| `parental lines` | ...cus's resistance effect. Twenty-eight F-1 hybrids and eight **[parental lines]** from a barley diallel study were inoculated with five... |
| `W x I` | 12 QTL for leaf Delta C-13 were detected in the **[W x I]** RILs. 5 QTL were detected in the M x H RILs. For the ... |
| `M x H` | ...were detected in the W x I RILs. 5 QTL were detected in the **[M x H]** RILs. For the W x I RILs, a major QTL was located on ... |
| `recombinant inbred line population` | A **[recombinant inbred line population]** derived from a cross between DZZ and KL10 was develop... |
| `F2 population` | ...tween lines with lnt2 mutant and wild-type alleles. A large **[F2 population]** was constructed and lnt2 was fine-mapped. |
| `F-2:8 RILs` | ...nduced premature senescence in cowpea. Genomic DNA from 113 **[F-2:8 RILs]** of drought-tolerant IT93K503-1 and susceptible CB46 g... |
| `142 sorghum parent lines` | The genetic structure of **[142 sorghum parent lines]** was analyzed using a model-based approach with SSR ma... |
| `F-2 population` | An **[F-2 population]** was generated from a cross between sweet sorghum cv. ... |
| `recombinant inbred lines` | ...variation and basis of A, E and A:E were described among 70 **[recombinant inbred lines]** (RILs) of sorghum. Experiment 1 used 40% and 80% of f... |
| `RILs` | ...E and A:E were described among 70 recombinant inbred lines (**[RILs]**) of sorghum. Experiment 1 used 40% and 80% of field c... |
| `Suphan Buri1 and the male-sterile line 03A` | .... These genotypes lacked the 779 bp band. The cross between **[Suphan Buri1 and the male-sterile line 03A]** produced a sterile male, confirming the marker's usef... |
| `F1 hybrid sorghum` | ...ouble-row crosses were tested. The root bleeding sap of the **[F1 hybrid sorghum]** showed high heterosis for soluble sugar content and a... |
| `Fulghum x Norline linkage map` | ...rs, four SNP markers, and one CAPS marker were added to the **[Fulghum x Norline linkage map]**. |
| `parent lines` | ...ical traits analyzed genetic diversity of 142 sweet sorghum **[parent lines]**. The lines were clustered into 5 groups based on agro... |
| `ZGMLEL` | ...Scssr03381-Scssr07759). It comes from the high-value parent **[ZGMLEL]**. |
| `F2 population from the cross Hatiexi No. 1 x Zhe5819` | ...ant analysis (BSA) was used to fine map the Blp1 gene in an **[F2 population from the cross Hatiexi No. 1 x Zhe5819]**. Based on SNP screening criteria, 77,542 polymorphic ... |
| `F-9:10 sorghum RILs` | ...stance to B. fusca and C. partellus in sorghum. It used 243 **[F-9:10 sorghum RILs]** from ICSV 745 and PB 15520-1 with 4,955 SNP markers. |
| `recombinant inbred line (RIL) population` | A **[recombinant inbred line (RIL) population]** of 189 individuals was derived from a cross between t... |
| `F-2:3 population` | The Sdwa5.1.1+ was confirmed in an **[F-2:3 population]** from the same cross and mapped to a 3.298-Kb region c... |

### 1.4 基因 (GENE)

| 实体文本 | 所在上下文片段 |
|---|---|
| `ABA Insensitive 5 (ABI5)` | **[ABA Insensitive 5 (ABI5)]** is a basic leucine zipper transcription factor. There is minimal research on the ABI5 family in foxtail millet. |
| `powdery mildew resistance genes` | Molecular markers identified chromosomal regions with **[powdery mildew resistance genes]** and estimated each locus's resistance effect. Twenty-... |
| `ribosome` | ...ted with increasing CC and RWC. Pathway analysis identified **[ribosome]** as a positive regulator of RWC and thermogenesis as a... |
| `GsNAC2` | **[GsNAC2]** was analyzed by bioinformatics methods. Sorghum plant... |
| `NAC` | Gs**[NAC]**2 was analyzed by bioinformatics methods. Sorghum plan... |
| `CqBIN2` | ...uinoa seedlings were treated with 24-epibrassinolide (EBR). **[CqBIN2]** was transiently transferred to the quinoa seedlings' ... |
| `SiLRR-RLK` | Several **[SiLRR-RLK]** genes are involved in stress response pathways. **[Si... |
| `SiPME67` | RT-qPCR verified the transcriptome data. Inhibiting **[SiPME67]** expression with antisense Oligonucleotide caused abno... |
| `FtbHLH2` | **[FtbHLH2]** localizes in the nucleus. Its overexpression in Arabidopsis increases cold tolerance. |
| `Hsf1` | ...tments. Hsf expression was not observed with ABA treatment. **[Hsf1]** showed high expression during high temperature and co... |
| `Hsf4` | ... high expression during high temperature and cold stresses. **[Hsf4]** and Hsf6 showed expression during salt stress. Hsf5, ... |
| `Hsf6` | ...ression during high temperature and cold stresses. Hsf4 and **[Hsf6]** showed expression during salt stress. Hsf5, **[Hsf6]*... |
| `Hsf5` | ...resses. Hsf4 and Hsf6 showed expression during salt stress. **[Hsf5]**, Hsf6, Hsf10, Hsf13, Hsf19, Hsf23 and Hsf25 showed ex... |
| `Hsf10` | ... and Hsf6 showed expression during salt stress. Hsf5, Hsf6, **[Hsf10]**, Hsf13, Hsf19, Hsf23 and Hsf25 showed expression duri... |
| `Hsf13` | ...f6 showed expression during salt stress. Hsf5, Hsf6, Hsf10, **[Hsf13]**, Hsf19, Hsf23 and Hsf25 showed expression during drou... |
| `Hsf19` | ...ed expression during salt stress. Hsf5, Hsf6, Hsf10, Hsf13, **[Hsf19]**, Hsf23 and Hsf25 showed expression during drought str... |
| `Hsf23` | ...ession during salt stress. Hsf5, Hsf6, Hsf10, Hsf13, Hsf19, **[Hsf23]** and Hsf25 showed expression during drought stress. |
| `Hsf25` | ...ing salt stress. Hsf5, Hsf6, Hsf10, Hsf13, Hsf19, Hsf23 and **[Hsf25]** showed expression during drought stress. |
| `PDCD4` | ...hyll content and leaf traits were linked to genes including **[PDCD4]**, LEA proteins, and Cytochrome P450. These findings pr... |
| `LEA proteins` | ...ntent and leaf traits were linked to genes including PDCD4, **[LEA proteins]**, and Cytochrome P450. These findings provide molecula... |

### 1.5 数量性状位点 (QTL)

| 实体文本 | 所在上下文片段 |
|---|---|
| `QTL regions` | ...llet samples from Xinjiang Academy using 1,304,248 SNPs. 77 **[QTL regions]** were detected across three environments. Analysis of ... |
| `QTL` | ...rtant for genetic improvement. This study aimed to identify **[QTL]** associated with bioenergy-related traits in sweet sor... |
| `QTLs` | Over 240 **[QTLs]** are reported for drought tolerance traits in sorghum ... |
| `stay green QTL regions` | ... Two stay green QTLs identified in this study correspond to **[stay green QTL regions]** in maize. |
| `metaQTL (MQTL)` | ...7 QTL for abiotic stress tolerance traits. It identified 79 **[metaQTL (MQTL)]**: 26 for drought, 11 for low temperature, 22 for salin... |
| `qBX3.1` | Two minor QTLs (**[qBX3.1]** and qBX7.1) for Brix (BX) were mapped on chromosomes ... |
| `qBX7.1` | Two minor QTLs (qBX3.1 and **[qBX7.1]**) for Brix (BX) were mapped on chromosomes 3 and 7. Th... |
| `qPH7.1/qBX7.1` | ...re mapped on chromosomes 3 and 7. The QTLs in two clusters (**[qPH7.1/qBX7.1]** and qPH7.1/qFBW7.1) overlapped for PH, FBW and BX. |
| `qPH7.1/qFBW7.1` | ...osomes 3 and 7. The QTLs in two clusters (qPH7.1/qBX7.1 and **[qPH7.1/qFBW7.1]**) overlapped for PH, FBW and BX. |
| `drought tolerance QTL` | A **[drought tolerance QTL]** on chromosome 2 was transferred from barley cultivar ... |
| `qPC5-1` | ... and Sobic.005G165700 were located in the same LD block for **[qPC5-1]**. Sobic.006G149650 and Sobic.006G149700 were located i... |
| `qPC6` | ...nd Sobic.006G149700 were located in different LD blocks for **[qPC6]**. |
| `adaptation-related QTL` | ..., Pc71, Pc91, and PcKM, and with adult-plant resistance and **[adaptation-related QTL]**. QTL on linkage groups Mrg03, Mrg08, and Mrg23 were i... |
| `QTLs for biological yield` | **[QTLs for biological yield]**, days to heading, and kernel weight on chromosome 2H;... |
| `QTL for harvest index` | ...yield, days to heading, and kernel weight on chromosome 2H; **[QTL for harvest index]** on 1H; QTLs for kernel weight on 2H, 4H, and 5H. For ... |
| `QTLs for kernel weight` | ...ernel weight on chromosome 2H; QTL for harvest index on 1H; **[QTLs for kernel weight]** on 2H, 4H, and 5H. For rainfall less than 450 mm, QTL... |
| `QTL for grain yield` | ...el weight on 2H, 4H, and 5H. For rainfall less than 450 mm, **[QTL for grain yield]** on 6H; QTLs for kernel weight on 2H and 5H; QTLs for ... |
| `QTLs for seed per head` | ...for grain yield on 6H; QTLs for kernel weight on 2H and 5H; **[QTLs for seed per head]** on 1H and 6H; QTL for days to heading on 2H. |
| `QTL for days to heading` | ...l weight on 2H and 5H; QTLs for seed per head on 1H and 6H; **[QTL for days to heading]** on 2H. |
| `QTL for DON` | **[QTL for DON]** were found on chromosomes 5C, 9D, 13A, 14D and unknow... |

### 1.6 分子标记 (MRK)

| 实体文本 | 所在上下文片段 |
|---|---|
| `SNPs` | ...oxtail millet samples from Xinjiang Academy using 1,304,248 **[SNPs]**. 77 QTL regions were detected across three environmen... |
| `Molecular markers` | **[Molecular markers]** identified chromosomal regions with powdery mildew re... |
| `Bmag606` | ... RILs, a major QTL was located on chromosome 3H near marker **[Bmag606]**. |
| `InDels` | Of 8,361 high-quality **[InDels]** longer than 20 bp developed as molecular markers, 180... |
| `EcoR1` | ...IT93K503-1 and susceptible CB46 genotypes was digested with **[EcoR1]**, HpaII, Mse1, or Msp1 restriction enzymes and amplifi... |
| `HpaII` | ...3-1 and susceptible CB46 genotypes was digested with EcoR1, **[HpaII]**, Mse1, or Msp1 restriction enzymes and amplified with... |
| `Mse1` | ... susceptible CB46 genotypes was digested with EcoR1, HpaII, **[Mse1]**, or Msp1 restriction enzymes and amplified with prime... |
| `Msp1` | ...ble CB46 genotypes was digested with EcoR1, HpaII, Mse1, or **[Msp1]** restriction enzymes and amplified with primers from 1... |
| `SSR markers` | ...parent lines was analyzed using a model-based approach with **[SSR markers]**. Forty-one **[SSR markers]** were selected from 103 m... |
| `Forty-one SSR markers` | ...was analyzed using a model-based approach with SSR markers. **[Forty-one SSR markers]** were selected from 103 markers. These markers generat... |
| `103 markers` | ... with SSR markers. Forty-one SSR markers were selected from **[103 markers]**. These markers generated 189 alleles, ranging from 2 ... |
| `AFLP markers` | The two **[AFLP markers]** were converted to STS markers. The STS markers are us... |
| `STS markers` | The two AFLP markers were converted to **[STS markers]**. The **[STS markers]** are useful for marker-assisted... |
| `molecular markers` | ... should consider groups clustered by agronomical traits and **[molecular markers]**. |
| `genetic map` | ...ghum cv. 'Erdurmus' and grain sorghum cv. 'Ogretmenoglu'. A **[genetic map]** was constructed from SNPs discovered by ddRAD-seq. |
| `primer pairs` | For sorghum SSR markers, 2,113 **[primer pairs]** were designed from 81,342 public genomic contigs. Scr... |
| `81,342 public genomic contigs` | ... sorghum SSR markers, 2,113 primer pairs were designed from **[81,342 public genomic contigs]**. Screening eight sorghum lines identified 1,758 polym... |
| `1,758 polymorphic primers` | ...c genomic contigs. Screening eight sorghum lines identified **[1,758 polymorphic primers]**. Of these, 1,710 SSR markers were predominantly polym... |
| `1,710 SSR markers` | ...rghum lines identified 1,758 polymorphic primers. Of these, **[1,710 SSR markers]** were predominantly polymorphic and detected from two ... |
| `LW7 marker` | Twenty-five sorghum accessions were evaluated. The **[LW7 marker]** identified accessions with the male sterility gene rf... |

### 1.7 染色体 (CHR)

| 实体文本 | 所在上下文片段 |
|---|---|
| `chromosomal regions` | Molecular markers identified **[chromosomal regions]** with powdery mildew resistance genes and estimated ea... |
| `chromosome 3H` | ... M x H RILs. For the W x I RILs, a major QTL was located on **[chromosome 3H]** near marker Bmag606. |
| `chromosome 1` | ...L populations. One co-located QTL for TGW was discovered on **[chromosome 1]**. Transcriptome analysis revealed 59 candidate genes w... |
| `chromosomes` | SNPs induced by EMS were unevenly distributed across all 18 **[chromosomes]**, with an average mutation frequency of 91.2 SNPs/Mb. ... |
| `chromosome` | SNPs induced by EMS were unevenly distributed across all 18 **[chromosome]**s, with an average mutation frequency of 91.2 SNPs/Mb.... |
| `chromosomes 3 and 7` | ...minor QTLs (qBX3.1 and qBX7.1) for Brix (BX) were mapped on **[chromosomes 3 and 7]**. The QTLs in two clusters (qPH7.1/qBX7.1 and qPH7.1/q... |
| `chromosome 2` | A drought tolerance QTL on **[chromosome 2]** was transferred from barley cultivar 'Tadmor' to cult... |
| `Mrg03` | ...esistance and adaptation-related QTL. QTL on linkage groups **[Mrg03]**, Mrg08, and Mrg23 were identified in regions not prev... |
| `Mrg08` | ...ce and adaptation-related QTL. QTL on linkage groups Mrg03, **[Mrg08]**, and Mrg23 were identified in regions not previously ... |
| `Mrg23` | ...tation-related QTL. QTL on linkage groups Mrg03, Mrg08, and **[Mrg23]** were identified in regions not previously associated ... |
| `A, B, C, and D oat genomes` | ...oids have AACCCCDD, AAAACCDD, or AABBCCDD compositions. The **[A, B, C, and D oat genomes]** differ in involvement in non-centromeric, intercalary... |
| `chromosome 2H` | ...for biological yield, days to heading, and kernel weight on **[chromosome 2H]**; QTL for harvest index on 1H; QTLs for kernel weight ... |
| `1H` | ...nd kernel weight on chromosome 2H; QTL for harvest index on **[1H]**; QTLs for kernel weight on 2H, 4H, and 5H. For rainfa... |
| `2H` | ...cal yield, days to heading, and kernel weight on chromosome **[2H]**; QTL for harvest index on 1H; QTLs for kernel weight ... |
| `4H` | ... QTL for harvest index on 1H; QTLs for kernel weight on 2H, **[4H]**, and 5H. For rainfall less than 450 mm, QTL for grain... |
| `5H` | ... harvest index on 1H; QTLs for kernel weight on 2H, 4H, and **[5H]**. For rainfall less than 450 mm, QTL for grain yield o... |
| `6H` | ...d 5H. For rainfall less than 450 mm, QTL for grain yield on **[6H]**; QTLs for kernel weight on 2H and 5H; QTLs for seed p... |
| `18 chromosomes` | ...chromosome-scale genome assembly of little millet comprises **[18 chromosomes]** and 59,045 genes. Eleven chromosomes are assembled fr... |
| `Eleven chromosomes` | ...of little millet comprises 18 chromosomes and 59,045 genes. **[Eleven chromosomes]** are assembled from telomere to telomere, revealing an... |
| `SBI-01` | ...identified for all traits and co-located to five locations: **[SBI-01]**, SBI-03, SBI-05, SBI-06 and SBI-10. QTL alleles from ... |

### 1.8 性状 (TRT)

| 实体文本 | 所在上下文片段 |
|---|---|
| `powdery mildew resistance` | Molecular markers identified chromosomal regions with **[powdery mildew resistance]** genes and estimated each locus's resistance effect. T... |
| `flowering time` | ...d with bioenergy-related traits in sweet sorghum, including **[flowering time]**, plant height, total biomass, stem diameter, stem moi... |
| `plant height` | ...-related traits in sweet sorghum, including flowering time, **[plant height]**, total biomass, stem diameter, stem moisture percenta... |
| `total biomass` | ...s in sweet sorghum, including flowering time, plant height, **[total biomass]**, stem diameter, stem moisture percentage, and brix. |
| `stem diameter` | ...hum, including flowering time, plant height, total biomass, **[stem diameter]**, stem moisture percentage, and brix. |
| `stem moisture percentage` | ...flowering time, plant height, total biomass, stem diameter, **[stem moisture percentage]**, and brix. |
| `brix` | ...total biomass, stem diameter, stem moisture percentage, and **[brix]**. |
| `CC` | Clust analysis found 2987 genes correlated with increasing **[CC]** and RWC. Pathway analysis identified ribosome as a po... |
| `RWC` | ...analysis found 2987 genes correlated with increasing CC and **[RWC]**. Pathway analysis identified ribosome as a positive r... |
| `thermogenesis` | ...ysis identified ribosome as a positive regulator of RWC and **[thermogenesis]** as a positive regulator of CC. |
| `drought tolerance traits` | Over 240 QTLs are reported for **[drought tolerance traits]** in sorghum for marker discovery. Identifying traits a... |
| `HT tolerance` | ...ding their physiological and genetic mechanisms may enhance **[HT tolerance]**. |
| `drought-resistant` | The **[drought-resistant]** cultivar JiaYan 2 (JIA2) and water-sensitive cultivar... |
| `water-sensitive` | The drought-resistant cultivar JiaYan 2 (JIA2) and **[water-sensitive]** cultivar BaYou 9 (BA9) were subjected to three water ... |
| `leaf Delta C-13` | 12 QTL for **[leaf Delta C-13]** were detected in the W x I RILs. 5 QTL were detected ... |
| `thousand grain weight` | This study identified 5 QTLs for **[thousand grain weight]** (TGW), 9 for grain length (GL), and 1 for grain width... |
| `TGW` | This study identified 5 QTLs for thousand grain weight (**[TGW]**), 9 for grain length (GL), and 1 for grain width (GW)... |
| `grain length` | ...dy identified 5 QTLs for thousand grain weight (TGW), 9 for **[grain length]** (GL), and 1 for grain width (GW) using data from 202 ... |
| `GL` | ...5 QTLs for thousand grain weight (TGW), 9 for grain length (**[GL]**), and 1 for grain width (GW) using data from 202 RIL ... |
| `grain width` | ...sand grain weight (TGW), 9 for grain length (GL), and 1 for **[grain width]** (GW) using data from 202 RIL populations. One co-loca... |

### 1.9 生育时期 (GST)

| 实体文本 | 所在上下文片段 |
|---|---|
| `booting stage` | ...ere subjected to three water gradient treatments during the **[booting stage]**: 30% field capacity (severe stress), 45% field capaci... |
| `flowering` | ...eather and a model crop for C4 gene research. Analyzing its **[flowering]** regulatory network is important for cultivating early... |
| `seedling` | ...sequencing analysis of foxtail millet pollen, ovule, glume, **[seedling]**, and root revealed 940 up-regulated genes in pollen. ... |
| `Early season` | **[Early season]** cold affects seed germination, seedling vigor, and ro... |
| `Late-season` | ...mination, seedling vigor, and root architecture in sorghum. **[Late-season]** frost reduces fertility, yield, and nutrition quality... |
| `flowering stage` | ...terosis for soluble sugar content and amino acid content at **[flowering stage]**, with average high-parent heterosis of 129.34% and 74... |
| `germination` | High salinity inhibited **[germination]** more at 10-20°C for both species. Alkali stress caused more stress at 25-35°C even at low concentration. |
| `germination stage` | ...oat germplasm resources with saline-alkali tolerance at the **[germination stage]** were screened. A regression equation for identifying ... |
| `cold sowing conditions` | The QTLs for frost survival and plant emergence under **[cold sowing conditions]** do not overlap. Genome-wide association studies ident... |
| `maturity stages` | ...wo novel QTL clusters controlled NUE traits at seedling and **[maturity stages]**. Genes related to NUE traits were predicted in the ma... |
| `15 DAP` | SiPSY1 transcription in **[15 DAP]** immature grains determined YPC in mature seeds. Selec... |
| `late heading` | ...r field conditions, transgressive segregation of DTH toward **[late heading]** was observed in the F2 population. |
| `seedling stage` | ...robust resistance against stripe rust infection at both the **[seedling stage]** and the adult stage upon inoculation with Puccinia st... |
| `adult stage` | ...st stripe rust infection at both the seedling stage and the **[adult stage]** upon inoculation with Puccinia striiformis f. sp. tri... |
| `Pre-anthesis` | ...hotosynthetic apparatus function by 63% due to PSII damage. **[Pre-anthesis]** was the most vulnerable stage to hydric stress, decre... |
| `post-anthesis` | ...f drought. 'Xiqiao-2' showed greater tolerance to long-term **[post-anthesis]** drought. 'Dingku-1' was less affected by short-term *... |
| `late growth phase` | ...hum aphid Melanaphis sacchari is an important insect in the **[late growth phase]** of sorghum (Sorghum bicolor). The mechanisms of sorgh... |
| `post-flowering` | In sorghum, stay-green is a trait for improving **[post-flowering]** drought tolerance. Genes in the introgressed QTL regi... |
| `heading stage` | ... RNA-seq revealed 2,293 and 2,338 DEGs between biparents at **[heading stage]** and grain filling stage. |
| `grain filling stage` | ...2,293 and 2,338 DEGs between biparents at heading stage and **[grain filling stage]**. |

### 1.10 非生物胁迫 (ABS)

| 实体文本 | 所在上下文片段 |
|---|---|
| `saline-alkali stress` | ...by bioinformatics methods. Sorghum plants were treated with **[saline-alkali stress]** solution at 2 weeks old. GsNAC2 belongs to the NAC ge... |
| `30% field capacity` | ...o three water gradient treatments during the booting stage: **[30% field capacity]** (severe stress), 45% field capacity (moderate stress)... |
| `severe stress` | ...nt treatments during the booting stage: 30% field capacity (**[severe stress]**), 45% field capacity (moderate stress), and 70% field... |
| `45% field capacity` | ...ring the booting stage: 30% field capacity (severe stress), **[45% field capacity]** (moderate stress), and 70% field capacity (normal wat... |
| `moderate stress` | ...ge: 30% field capacity (severe stress), 45% field capacity (**[moderate stress]**), and 70% field capacity (normal water supply). After... |
| `70% field capacity` | ... (severe stress), 45% field capacity (moderate stress), and **[70% field capacity]** (normal water supply). After 7 days, root samples wer... |
| `normal water supply` | ...% field capacity (moderate stress), and 70% field capacity (**[normal water supply]**). After 7 days, root samples were collected for trans... |
| `drought` | ...SiLRR-RLK genes show differential expression in response to **[drought]**, salinity, and pathogen infection. |
| `salinity` | ... genes show differential expression in response to drought, **[salinity]**, and pathogen infection. |
| `pathogen infection` | ...fferential expression in response to drought, salinity, and **[pathogen infection]**. |
| `ABA treatment` | ...tic stress treatments. Hsf expression was not observed with **[ABA treatment]**. Hsf1 showed high expression during high temperature ... |
| `cold stresses` | ...nt. Hsf1 showed high expression during high temperature and **[cold stresses]**. Hsf4 and Hsf6 showed expression during salt stress. ... |
| `salt stress` | ...e and cold stresses. Hsf4 and Hsf6 showed expression during **[salt stress]**. Hsf5, Hsf6, Hsf10, Hsf13, Hsf19, Hsf23 and Hsf25 sho... |
| `drought stress` | ...f10, Hsf13, Hsf19, Hsf23 and Hsf25 showed expression during **[drought stress]**. |
| `saline-alkali treatment` | ...sed GR and GSH-Px activities and accumulated more GSH after **[saline-alkali treatment]**. |
| `lactofen` | ...mely strong. Jingu 21 showed extremely strong resistance to **[lactofen]**, butachlor, and anilofos. |
| `butachlor` | ...g. Jingu 21 showed extremely strong resistance to lactofen, **[butachlor]**, and anilofos. |
| `anilofos` | ...wed extremely strong resistance to lactofen, butachlor, and **[anilofos]**. |
| `Drought` | **[Drought]** tolerance traits, stay green, and grain yield have be... |
| `mineral toxicity and deficiency` | ...mperature, 22 for salinity, 17 for water-logging, and 3 for **[mineral toxicity and deficiency]**. The MQTL distribution was similar to the initial QTL... |

### 1.11 生物胁迫 (BIS)

| 实体文本 | 所在上下文片段 |
|---|---|
| `E. graminis` | ... barley diallel study were inoculated with five isolates of **[E. graminis]**. |
| `salmonella infection` | ...metabolism, beta-alanine metabolism, vitamin B6 metabolism, **[salmonella infection]**, chloroalkane and chloroalkene degradation, and limon... |
| `anthracnose` | ...ated with C. graminicola isolates showed that resistance to **[anthracnose]** in sorghum accession G 73 segregated as a recessive t... |
| `crown rust` | ...3 were identified in regions not previously associated with **[crown rust]** resistance. |
| `CLS` | BC lines had moderate to high **[CLS]** and PM resistance compared to susceptible parent KING... |
| `PM` | BC lines had moderate to high CLS and **[PM]** resistance compared to susceptible parent KING. BC li... |
| `Anthracnose` | **[Anthracnose]**, caused by Colletotrichum sublineolum, is a destructi... |
| `Colletotrichum sublineolum` | Anthracnose, caused by **[Colletotrichum sublineolum]**, is a destructive disease of sorghum (Sorghum bicolor... |
| `Striga` | Chromosomes 1, 2, 3, 4, and 6 harbored SNPs significant for **[Striga]** tolerance in sorghum. Significant SNPs were found for... |
| `BSR` | ... time-consuming. We used 105 F-3 lines from a cross between **[BSR]**-resistant 'Syumari' and susceptible 'Buchishoryukei-1... |
| `biotic stresses` | ...OS homeostasis, accumulating H2O2 and O2- under abiotic and **[biotic stresses]**, inhibiting pathogen colonization. |
| `pathogen colonization` | ... H2O2 and O2- under abiotic and biotic stresses, inhibiting **[pathogen colonization]**. |
| `immune response` | ...th and development regulation, drought stress response, and **[immune response]**. SiPIP2;1 and SiEhd2 were identified as interactors o... |
| `blast` | ...entified as interactors of SiUBC39, explaining its roles in **[blast]** resistance and flowering time control. Domestication ... |
| `stripe rust infection` | LCR4 exhibited robust resistance against **[stripe rust infection]** at both the seedling stage and the adult stage upon i... |
| `Puccinia striiformis f. sp. tritici (Pst) race V26` | ...he seedling stage and the adult stage upon inoculation with **[Puccinia striiformis f. sp. tritici (Pst) race V26]** and mixed Pst races, respectively. Genetic analysis e... |
| `mixed Pst races` | ...with Puccinia striiformis f. sp. tritici (Pst) race V26 and **[mixed Pst races]**, respectively. Genetic analysis elucidated that the t... |
| `Septoria avenae f. sp. avenae` | The cultivation of oats has been affected by **[Septoria avenae f. sp. avenae]**, septoria leaf blotch disease. |
| `septoria leaf blotch disease` | The cultivation of oats has been affected by Septoria avenae f. sp. avenae, **[septoria leaf blotch disease]**. |
| `Usi infection` | qRT-PCR results indicated that 30 genes responded to **[Usi infection]**. 17 genes showed strong association with rust resista... |

### 1.12 育种方法 (BM)

| 实体文本 | 所在上下文片段 |
|---|---|
| `genome-wide association study` | A **[genome-wide association study]** analyzed 425 foxtail millet samples from Xinjiang Aca... |
| `Marker-assisted breeding` | **[Marker-assisted breeding]** is important for genetic improvement. This study aime... |
| `transcriptome` | ...ater supply). After 7 days, root samples were collected for **[transcriptome]** and proteome analyses. |
| `marker-assisted selection` | ...o-segregating genes. This identification provides tools for **[marker-assisted selection]**. |
| `Transcriptome analysis` | ... One co-located QTL for TGW was discovered on chromosome 1. **[Transcriptome analysis]** revealed 59 candidate genes with significant expressi... |
| `genotyping-by-sequencing` | ...developed. A high-density genetic map was constructed using **[genotyping-by-sequencing]** data, and QTL analysis was performed across five envi... |
| `GWAS` | **[GWAS]** identified MTAs for oat nutritional quality, agronomi... |
| `Genome-wide association studies (GWAS` | ...grain number (GrN) per plant, and 1000-grain weight (TGrW). **[Genome-wide association studies (GWAS]**) were conducted. Broad-sense heritability for biomass... |
| `EMS` | SNPs induced by **[EMS]** were unevenly distributed across all 18 chromosomes, ... |
| `GA(3)-treated` | ... 3) under salt stress. Whole-transcriptome analysis between **[GA(3)-treated]** and control sorghum leaves under salt stress identifi... |
| `GA(3) treatment` | ...cRNAs, 7 DE-circRNAs, and 26 DE-miRNAs in sorghum following **[GA(3) treatment]**. |
| `association mapping` | ...ty, yield, and nutrition quality and content in sorghum. An **[association mapping]** study was conducted to delineate the genetics of earl... |
| `RNA-seq` | ...ormone- and stress-responsive cis-elements. Tissue-specific **[RNA-seq]** data showed root-enriched expression of SbDIR2, SbDIR... |
| `genome re-sequencing` | ... variation were identified by integrating transcriptome and **[genome re-sequencing]** data. TFs including MYB, MADS, and LBD genes and RLKs... |
| `map-based cloning` | ...sisted selection of plants with non-brittle pedicel and for **[map-based cloning]** of the non-brittle pedicel gene. |
| `Transcriptome` | **[Transcriptome]** data showed high expression of genes VfbZIP1, VfbZIP2... |
| `PVX vector` | ...bZIP5. Ectopic overexpression of VfbZIP5 in tobacco using a **[PVX vector]** enhanced drought tolerance. |
| `proteomics` | ...dopsis thaliana. Advances in metabolomics, transcriptomics, **[proteomics]**, phenomics, population genomics and pangenomics expan... |
| `ddRAD-seq` | ...glu'. A genetic map was constructed from SNPs discovered by **[ddRAD-seq]**. |
| `Sanger sequencing` | ...nd Ca07571, as candidates for drought response in chickpea. **[Sanger sequencing]**, DArT, molecular markers, RT-qPCR, and field trial se... |

## 2. 关系抽取示例 (Relation Few-shot Examples)

### 2.1 包含 (CON)

| 头实体 (Head) | 尾实体 (Tail) | 所在上下文片段 |
|---|---|---|
| `(CROP) foxtail millet` | `(QTL) QTL regions` | A genome-wide association study analyzed 425 **[foxtail millet]** samples from Xinjiang Academy using 1,304,248 SNPs. 77 **[QTL regions]** were detect... |
| `(CROSS) F-1 hybrids` | `(CROP) barley` | Molecular markers identified chromosomal regions with powdery mildew resistance genes and estimated each locus's resistance effect. Twenty-eight **[F-... |
| `(CROSS) parental lines` | `(CROP) barley` | Molecular markers identified chromosomal regions with powdery mildew resistance genes and estimated each locus's resistance effect. Twenty-eight F-1 h... |
| `(GENE) GsNAC2` | `(GENE) NAC` | **[Gs**[NAC]**2]** was analyzed by bioinformatics methods. Sorghum plants were treated with saline-alkali stress solution at 2 weeks old. **[Gs**[NAC]... |
| `(ABS) 30% field capacity` | `(ABS) severe stress` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) 45% field capacity` | `(ABS) moderate stress` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) 70% field capacity` | `(ABS) normal water supply` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(CROSS) W x I` | `(VAR) RILs` | 12 QTL for leaf Delta C-13 were detected in the **[W x I]** **[RILs]**. 5 QTL were detected in the M x H **[RILs]**. For the **[W x I]** **[RILs]**, a... |
| `(CROSS) M x H` | `(VAR) RILs` | 12 QTL for leaf Delta C-13 were detected in the W x I **[RILs]**. 5 QTL were detected in the **[M x H]** **[RILs]**. For the W x I **[RILs]**, a major... |
| `(CROP) Tartary buckwheat` | `(VAR) This` | Comparative genomics and QTL analysis revealed the genetic basis of the easily dehulled trait in a particular variety. **[This]** variety was artifici... |
| `(CROP) maize` | `(QTL) stay green QTL regions` | The stay green line SC56 is from a different source than B35. Two stay green QTLs identified in this study correspond to **[stay green QTL regions]** ... |
| `(VAR) sorghum (Jitian 3)` | `(CROP) sorghum` | A GA(3) concentration of 50 mg/L is optimal for **[**[sorghum]** (Jitian 3)]** under salt stress. Whole-transcriptome analysis between GA(3)-treated a... |
| `(CROP) cowpea` | `(VAR) susceptible CB46` | Restriction site polymorphisms were used to investigate co-location of candidate genes with QTL for seedling drought stress-induced premature senescen... |
| `(CROSS) F-2:8 RILs` | `(VAR) drought-tolerant IT93K503-1` | Restriction site polymorphisms were used to investigate co-location of candidate genes with QTL for seedling drought stress-induced premature senescen... |
| `(CROSS) F-2:8 RILs` | `(VAR) susceptible CB46` | Restriction site polymorphisms were used to investigate co-location of candidate genes with QTL for seedling drought stress-induced premature senescen... |
| `(CROP) sorghum` | `(CROSS) 142 sorghum parent lines` | The genetic structure of 142 **[sorghum]** parent lines was analyzed using a model-based approach with SSR markers. Forty-one SSR markers were selecte... |
| `(MRK) 103 markers` | `(MRK) Forty-one SSR markers` | The genetic structure of 142 sorghum parent lines was analyzed using a model-based approach with SSR markers. **[Forty-one SSR markers]** were selecte... |
| `(CROP) sorghum` | `(VAR) G 73` | F-1 and F-2 plants inoculated with C. graminicola isolates showed that resistance to anthracnose in **[sorghum]** accession **[G 73]** segregated as a... |
| `(CROP) sorghum` | `(VAR) HC 136` | F-1 and F-2 plants inoculated with C. graminicola isolates showed that resistance to anthracnose in **[sorghum]** accession G 73 segregated as a reces... |
| `(CROP) sweet sorghum` | `(VAR) cv. 'Erdurmus'` | An F-2 population was generated from a cross between **[sweet sorghum]** **[cv. 'Erdurmus']** and grain sorghum cv. 'Ogretmenoglu'. A genetic map was ... |

### 2.2 具有 (HAS)

| 头实体 (Head) | 尾实体 (Tail) | 所在上下文片段 |
|---|---|---|
| `(CROP) sweet sorghum` | `(TRT) flowering time` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify QTL associated with bioenergy-related traits in **[sweet s... |
| `(CROP) sweet sorghum` | `(TRT) plant height` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify QTL associated with bioenergy-related traits in **[sweet s... |
| `(CROP) sweet sorghum` | `(TRT) total biomass` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify QTL associated with bioenergy-related traits in **[sweet s... |
| `(CROP) sweet sorghum` | `(TRT) stem diameter` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify QTL associated with bioenergy-related traits in **[sweet s... |
| `(CROP) sweet sorghum` | `(TRT) stem moisture percentage` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify QTL associated with bioenergy-related traits in **[sweet s... |
| `(CROP) sweet sorghum` | `(TRT) brix` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify QTL associated with bioenergy-related traits in **[sweet s... |
| `(CROP) sorghum` | `(TRT) drought tolerance traits` | Over 240 QTLs are reported for **[drought tolerance traits]** in **[sorghum]** for marker discovery. Identifying traits and understanding their physio... |
| `(VAR) JiaYan 2` | `(TRT) drought-resistant` | The **[drought-resistant]** cultivar **[JiaYan 2]** (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatment... |
| `(VAR) JIA2` | `(TRT) drought-resistant` | The **[drought-resistant]** cultivar JiaYan 2 (**[JIA2]**) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatment... |
| `(VAR) BaYou 9` | `(TRT) water-sensitive` | The drought-resistant cultivar JiaYan 2 (JIA2) and **[water-sensitive]** cultivar **[BaYou 9]** (BA9) were subjected to three water gradient treatment... |
| `(VAR) BA9` | `(TRT) water-sensitive` | The drought-resistant cultivar JiaYan 2 (JIA2) and **[water-sensitive]** cultivar BaYou 9 (**[BA9]**) were subjected to three water gradient treatment... |
| `(VAR) Jingu 21` | `(TRT) resistance to 31 herbicides` | **[Jingu 21]** **[resistance to 31 herbicides]** was categorized into five levels: extremely weak, weak, moderate, strong, and extremely strong. **[Ji... |
| `(VAR) Jingu 21` | `(TRT) extremely strong` | **[Jingu 21]** resistance to 31 herbicides was categorized into five levels: extremely weak, weak, moderate, strong, and **[extremely strong]**. **[Ji... |
| `(VAR) susceptible CB46` | `(TRT) seedling drought stress-induced premature` | Restriction site polymorphisms were used to investigate co-location of candidate genes with QTL for **[seedling drought stress-induced premature]** se... |
| `(CROP) cowpea` | `(VAR) drought-tolerant IT93K503-1` | Restriction site polymorphisms were used to investigate co-location of candidate genes with QTL for seedling drought stress-induced premature senescen... |
| `(CROP) sorghum` | `(TRT) seed germination` | Early season cold affects **[seed germination]**, seedling vigor, and root architecture in **[sorghum]**. Late-season frost reduces fertility, yield, ... |
| `(CROP) sorghum` | `(TRT) seedling vigor` | Early season cold affects seed germination, **[seedling vigor]**, and root architecture in **[sorghum]**. Late-season frost reduces fertility, yield, ... |
| `(CROP) sorghum` | `(TRT) fertility` | Early season cold affects seed germination, seedling vigor, and root architecture in **[sorghum]**. Late-season frost reduces **[fertility]**, yield, ... |
| `(CROP) sorghum` | `(TRT) yield` | Early season cold affects seed germination, seedling vigor, and root architecture in **[sorghum]**. Late-season frost reduces fertility, **[yield]**, ... |
| `(CROP) sorghum` | `(TRT) nutrition quality and content` | Early season cold affects seed germination, seedling vigor, and root architecture in **[sorghum]**. Late-season frost reduces fertility, yield, and **... |

### 2.3 定位于 (LOI)

| 头实体 (Head) | 尾实体 (Tail) | 所在上下文片段 |
|---|---|---|
| `(MRK) SNPs` | `(QTL) QTL regions` | A genome-wide association study analyzed 425 foxtail millet samples from Xinjiang Academy using 1,304,248 **[SNPs]**. 77 **[QTL regions]** were detect... |
| `(MRK) Molecular markers` | `(CHR) chromosomal regions` | **[Molecular markers]** identified **[chromosomal regions]** with powdery mildew resistance genes and estimated each locus's resistance effect. Twenty... |
| `(GENE) powdery mildew resistance genes` | `(TRT) powdery mildew resistance` | Molecular markers identified chromosomal regions with **[**[powdery mildew resistance]** genes]** and estimated each locus's resistance effect. Twenty... |
| `(QTL) QTL` | `(TRT) flowering time` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify **[QTL]** associated with bioenergy-related traits in swee... |
| `(QTL) QTL` | `(TRT) plant height` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify **[QTL]** associated with bioenergy-related traits in swee... |
| `(QTL) QTL` | `(TRT) total biomass` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify **[QTL]** associated with bioenergy-related traits in swee... |
| `(QTL) QTL` | `(TRT) stem diameter` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify **[QTL]** associated with bioenergy-related traits in swee... |
| `(QTL) QTL` | `(TRT) stem moisture percentage` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify **[QTL]** associated with bioenergy-related traits in swee... |
| `(QTL) QTL` | `(TRT) brix` | Marker-assisted breeding is important for genetic improvement. This study aimed to identify **[QTL]** associated with bioenergy-related traits in swee... |
| `(QTL) QTLs` | `(TRT) drought tolerance traits` | Over 240 **[QTLs]** are reported for **[drought tolerance traits]** in sorghum for marker discovery. Identifying traits and understanding their physio... |
| `(QTL) QTL` | `(TRT) leaf Delta C-13` | 12 **[QTL]** for **[leaf Delta C-13]** were detected in the W x I RILs. 5 **[QTL]** were detected in the M x H RILs. For the W x I RILs, a major **[QT... |
| `(QTL) QTL` | `(CHR) chromosome 3H` | 12 **[QTL]** for leaf Delta C-13 were detected in the W x I RILs. 5 **[QTL]** were detected in the M x H RILs. For the W x I RILs, a major **[QTL]** w... |
| `(MRK) Bmag606` | `(CHR) chromosome 3H` | 12 QTL for leaf Delta C-13 were detected in the W x I RILs. 5 QTL were detected in the M x H RILs. For the W x I RILs, a major QTL was located on **[c... |
| `(MRK) Bmag606` | `(QTL) QTL` | 12 **[QTL]** for leaf Delta C-13 were detected in the W x I RILs. 5 **[QTL]** were detected in the M x H RILs. For the W x I RILs, a major **[QTL]** w... |
| `(QTL) QTLs` | `(TRT) thousand grain weight` | This study identified 5 **[QTLs]** for **[thousand grain weight]** (TGW), 9 for grain length (GL), and 1 for grain width (GW) using data from 202 RIL ... |
| `(QTL) QTL` | `(TRT) thousand grain weight` | This study identified 5 **[QTL]**s for **[thousand grain weight]** (TGW), 9 for grain length (GL), and 1 for grain width (GW) using data from 202 RIL ... |
| `(QTL) QTLs` | `(TRT) grain length` | This study identified 5 **[QTLs]** for thousand grain weight (TGW), 9 for **[grain length]** (GL), and 1 for grain width (GW) using data from 202 RIL ... |
| `(QTL) QTL` | `(TRT) grain length` | This study identified 5 **[QTL]**s for thousand grain weight (TGW), 9 for **[grain length]** (GL), and 1 for grain width (GW) using data from 202 RIL ... |
| `(QTL) QTLs` | `(TRT) grain width` | This study identified 5 **[QTLs]** for thousand grain weight (TGW), 9 for grain length (GL), and 1 for **[grain width]** (GW) using data from 202 RIL ... |
| `(QTL) QTL` | `(TRT) grain width` | This study identified 5 **[QTL]**s for thousand grain weight (TGW), 9 for grain length (GL), and 1 for **[grain width]** (GW) using data from 202 RIL ... |

### 2.4 影响 (AFF)

| 头实体 (Head) | 尾实体 (Tail) | 所在上下文片段 |
|---|---|---|
| `(BIS) E. graminis` | `(TRT) powdery mildew resistance` | Molecular markers identified chromosomal regions with **[powdery mildew resistance]** genes and estimated each locus's resistance effect. Twenty-eight... |
| `(GENE) ribosome` | `(TRT) RWC` | Clust analysis found 2987 genes correlated with increasing CC and **[RWC]**. Pathway analysis identified **[ribosome]** as a positive regulator of **[... |
| `(TRT) thermogenesis` | `(TRT) CC` | Clust analysis found 2987 genes correlated with increasing **[CC]** and RWC. Pathway analysis identified ribosome as a positive regulator of RWC and *... |
| `(ABS) drought` | `(GENE) SiLRR-RLK` | Several **[SiLRR-RLK]** genes are involved in stress response pathways. **[SiLRR-RLK]** genes show differential expression in response to **[drought]*... |
| `(ABS) salinity` | `(GENE) SiLRR-RLK` | Several **[SiLRR-RLK]** genes are involved in stress response pathways. **[SiLRR-RLK]** genes show differential expression in response to drought, **[... |
| `(ABS) pathogen infection` | `(GENE) SiLRR-RLK` | Several **[SiLRR-RLK]** genes are involved in stress response pathways. **[SiLRR-RLK]** genes show differential expression in response to drought, sal... |
| `(ABS) ABA treatment` | `(GENE) Hsf1` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with **[ABA treatment]**. **[Hsf1]** showed high expression ... |
| `(ABS) cold stresses` | `(GENE) Hsf1` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. **[Hsf1]** showed high expression during... |
| `(ABS) salt stress` | `(GENE) Hsf4` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) salt stress` | `(GENE) Hsf6` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) drought stress` | `(GENE) Hsf6` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) drought stress` | `(GENE) Hsf5` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) drought stress` | `(GENE) Hsf10` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) drought stress` | `(GENE) Hsf13` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) drought stress` | `(GENE) Hsf19` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) drought stress` | `(GENE) Hsf23` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(ABS) drought stress` | `(GENE) Hsf25` | Sorghum plants were exposed to abiotic stress treatments. Hsf expression was not observed with ABA treatment. Hsf1 showed high expression during high ... |
| `(GENE) GsNAC2` | `(GENE) glutathione biosynthesis` | **[GsNAC2]** overexpression upregulated key **[glutathione biosynthesis]** genes. It increased GR and GSH-Px activities and accumulated more GSH after... |
| `(GENE) GsNAC2` | `(GENE) GR` | **[GsNAC2]** overexpression upregulated key glutathione biosynthesis genes. It increased **[GR]** and GSH-Px activities and accumulated more GSH after... |
| `(GENE) GsNAC2` | `(GENE) GSH-Px` | **[GsNAC2]** overexpression upregulated key glutathione biosynthesis genes. It increased GR and **[GSH-Px]** activities and accumulated more GSH after... |

### 2.5 发生于 (OCI)

| 头实体 (Head) | 尾实体 (Tail) | 所在上下文片段 |
|---|---|---|
| `(ABS) 30% field capacity` | `(GST) booting stage` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) severe stress` | `(GST) booting stage` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) 45% field capacity` | `(GST) booting stage` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) moderate stress` | `(GST) booting stage` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) 70% field capacity` | `(GST) booting stage` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) normal water supply` | `(GST) booting stage` | The drought-resistant cultivar JiaYan 2 (JIA2) and water-sensitive cultivar BaYou 9 (BA9) were subjected to three water gradient treatments during the... |
| `(ABS) early season cold` | `(GST) Early season` | **[Early season]** cold affects seed germination, seedling vigor, and root architecture in sorghum. Late-season frost reduces fertility, yield, and nu... |
| `(ABS) late-season frost` | `(GST) Late-season` | Early season cold affects seed germination, seedling vigor, and root architecture in sorghum. **[Late-season]** frost reduces fertility, yield, and nu... |
| `(TRT) soluble sugar content` | `(GST) flowering stage` | Six sterile and six restorer lines of sorghum and 36 hybrid sorghum combinations from incomplete double-row crosses were tested. The root bleeding sap... |
| `(TRT) amino acid content` | `(GST) flowering stage` | Six sterile and six restorer lines of sorghum and 36 hybrid sorghum combinations from incomplete double-row crosses were tested. The root bleeding sap... |
| `(ABS) High salinity` | `(GST) germination` | **[High salinity]** inhibited **[germination]** more at 10-20°C for both species. Alkali stress caused more stress at 25-35°C even at low concentratio... |
| `(TRT) High salinity inhibited germination` | `(GST) germination` | **[High salinity inhibited **[germination]**]** more at 10-20°C for both species. Alkali stress caused more stress at 25-35°C even at low concentratio... |
| `(TRT) saline-alkali tolerance` | `(GST) germination stage` | Cluster analysis classified 524 oat germplasm resources into five groups. 174 oat germplasm resources with **[saline-alkali tolerance]** at the **[ger... |
| `(TRT) frost survival` | `(GST) cold sowing conditions` | The QTLs for **[frost survival]** and plant emergence under **[cold sowing conditions]** do not overlap. Genome-wide association studies identified fo... |
| `(TRT) plant emergence` | `(GST) cold sowing conditions` | The QTLs for frost survival and **[plant emergence]** under **[cold sowing conditions]** do not overlap. Genome-wide association studies identified fo... |
| `(TRT) NUE traits` | `(GST) seedling` | Two novel QTL clusters controlled **[NUE traits]** at **[seedling]** and maturity stages. Genes related to **[NUE traits]** were predicted in the majo... |
| `(TRT) NUE traits` | `(GST) maturity stages` | Two novel QTL clusters controlled **[NUE traits]** at seedling and **[maturity stages]**. Genes related to **[NUE traits]** were predicted in the majo... |
| `(TRT) transgressive segregation of DTH toward late heading` | `(GST) late heading` | A QTL-seq analysis was conducted to identify genomic regions regulating days to heading (DTH). The analysis used an F2 population derived from crosses... |
| `(BIS) stripe rust infection` | `(GST) seedling stage` | LCR4 exhibited robust resistance against **[stripe rust infection]** at both the **[seedling stage]** and the adult stage upon inoculation with Puccin... |
| `(BIS) stripe rust infection` | `(GST) adult stage` | LCR4 exhibited robust resistance against **[stripe rust infection]** at both the seedling stage and the **[adult stage]** upon inoculation with Puccin... |

### 2.6 采用 (USE)

| 头实体 (Head) | 尾实体 (Tail) | 所在上下文片段 |
|---|---|---|
| `(CROP) sweet sorghum` | `(BM) Marker-assisted breeding` | **[Marker-assisted breeding]** is important for genetic improvement. This study aimed to identify QTL associated with bioenergy-related traits in **[s... |
| `(BM) GA(3)-treated` | `(VAR) sorghum (Jitian 3)` | A GA(3) concentration of 50 mg/L is optimal for **[sorghum (Jitian 3)]** under salt stress. Whole-transcriptome analysis between **[GA(3)-treated]** a... |
| `(CROSS) 142 sorghum parent lines` | `(MRK) SSR markers` | The genetic structure of **[142 sorghum parent lines]** was analyzed using a model-based approach with **[SSR markers]**. Forty-one **[SSR markers]** ... |
| `(MRK) AFLP markers` | `(MRK) STS markers` | The two **[AFLP markers]** were converted to **[STS markers]**. The **[STS markers]** are useful for marker-assisted selection of plants with non-brit... |
| `(CROP) tobacco` | `(BM) PVX vector` | Transcriptome data showed high expression of genes VfbZIP1, VfbZIP2, VfbZIP5, VfbZIP7, VfbZIP15, VfbZIP17, and VfbZIP18 in a drought-tolerant cultivar... |
| `(MRK) SNPs` | `(BM) ddRAD-seq` | An F-2 population was generated from a cross between sweet sorghum cv. 'Erdurmus' and grain sorghum cv. 'Ogretmenoglu'. A genetic map was constructed ... |
| `(VAR) eight sorghum lines` | `(MRK) 1,758 polymorphic primers` | For sorghum SSR markers, 2,113 primer pairs were designed from 81,342 public genomic contigs. Screening **[eight sorghum lines]** identified **[1,758 ... |
| `(MRK) functional markers` | `(BM) marker-assisted selection` | Sweet sorghum accumulates sugars in the stem parenchyma. Soluble acid invertase (SAI) is involved in sucrose accumulation. Characterization of SAI gen... |
| `(BM) Integrative breeding` | `(TRT) early maturity` | **[Integrative breeding]** targets **[early maturity]**, high harvest index, and water use efficiency (WUE) to improve sorghum productivity and mitiga... |
| `(BM) Integrative breeding` | `(TRT) high harvest index` | **[Integrative breeding]** targets early maturity, **[high harvest index]**, and water use efficiency (WUE) to improve sorghum productivity and mitiga... |
| `(BM) Integrative breeding` | `(TRT) water use efficiency (WUE)` | **[Integrative breeding]** targets early maturity, high harvest index, and **[water use efficiency (WUE)]** to improve sorghum productivity and mitiga... |
| `(VAR) EMS-mutagenized population` | `(BM) EMS-mutagenized` | An **[**[EMS-mutagenized]** population]** was created in the barley landrace TX9425. A TILLING population of 2000 M-2 lines was constructed using CEL ... |
| `(VAR) TILLING population` | `(BM) CEL I enzyme` | An EMS-mutagenized population was created in the barley landrace TX9425. A **[TILLING population]** of 2000 M-2 lines was constructed using **[CEL I e... |
| `(VAR) TILLING population` | `(BM) polyacrylamide electrophoresis` | An EMS-mutagenized population was created in the barley landrace TX9425. A **[TILLING population]** of 2000 M-2 lines was constructed using CEL I enzy... |
| `(CROP) foxtail millet` | `(BM) marker-assisted selection` | Identified MTAs have a pyramiding effect important for breeding. Desirable alleles and superior genotypes are valuable for **[foxtail millet]** improv... |
| `(VAR) Longli-4` | `(BM) ethyl methanesulfonate` | The '**[Longli-4]**' variety was treated with **[ethyl methanesulfonate]** (EMS) at 0.8% for 8 h. |
| `(VAR) Longli-4` | `(BM) EMS` | The '**[Longli-4]**' variety was treated with ethyl methanesulfonate (**[EMS]**) at 0.8% for 8 h. |
| `(BM) marker-assisted selection (MAS)` | `(MRK) RFLP` | QTLs for kernel area, kernel length, kernel width, and groat percentage were mapped in two populations of 137 recombinant inbred lines using **[RFLP]*... |
| `(BM) marker-assisted selection (MAS)` | `(MRK) AFLP` | QTLs for kernel area, kernel length, kernel width, and groat percentage were mapped in two populations of 137 recombinant inbred lines using RFLP and ... |
| `(VAR) recombinant inbred lines` | `(BM) Genotyping-by-Sequencing` | This study constructed **[recombinant inbred lines]** (RILs) using cultivated species and wild buckwheat. 84,521 SNP markers were identified by **[Gen... |

