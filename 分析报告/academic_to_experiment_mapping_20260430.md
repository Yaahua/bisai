# 学术方法到 bisai 仓库的实验映射

## 1. 方向混淆矩阵 Top 项

|类型|反向类型|训练数|反向训练数|v44数|v44反向数|判断|
|---|---|---:|---:|---:|---:|---|
|ABS-AFF-TRT|TRT-AFF-ABS|285|1|163|0|方向较稳定，谨慎删除|
|QTL-LOI-TRT|TRT-LOI-QTL|224|0|117|0|方向较稳定，谨慎删除|
|CROP-CON-VAR|VAR-CON-CROP|222|2|69|0|方向较稳定，谨慎删除|
|GENE-AFF-TRT|TRT-AFF-GENE|177|3|86|1|方向较稳定，谨慎删除|
|CROP-HAS-TRT|TRT-HAS-CROP|165|0|61|0|方向较稳定，谨慎删除|
|ABS-AFF-GENE|GENE-AFF-ABS|91|15|71|0|方向较稳定，谨慎删除|
|GENE-LOI-TRT|TRT-LOI-GENE|85|0|25|0|方向较稳定，谨慎删除|
|MRK-LOI-TRT|TRT-LOI-MRK|67|0|22|0|方向较稳定，谨慎删除|
|CROP-CON-GENE|GENE-CON-CROP|59|2|14|0|方向较稳定，谨慎删除|
|TRT-AFF-TRT|TRT-AFF-TRT|48|48|15|15|方向较稳定，谨慎删除|
|GENE-CON-GENE|GENE-CON-GENE|38|38|17|17|方向较稳定，谨慎删除|
|BM-USE-VAR|VAR-USE-BM|1|41|0|8||
|ABS-OCI-GST|GST-OCI-ABS|33|0|8|0|方向较稳定，谨慎删除|
|BM-AFF-TRT|TRT-AFF-BM|33|0|2|0|方向较稳定，谨慎删除|
|CROSS-CON-VAR|VAR-CON-CROSS|28|8|7|0|方向较稳定，谨慎删除|
|CROP-CON-CROP|CROP-CON-CROP|21|21|13|13|方向较稳定，谨慎删除|
|GENE-AFF-GENE|GENE-AFF-GENE|26|26|5|5|方向较稳定，谨慎删除|
|BIS-AFF-TRT|TRT-AFF-BIS|24|1|5|0|方向较稳定，谨慎删除|
|QTL-AFF-TRT|TRT-AFF-QTL|26|0|2|0|方向较稳定，谨慎删除|
|GENE-LOI-MRK|MRK-LOI-GENE|2|22|5|2|v44 存在但训练反向更强，优先做方向验证|
|ABS-AFF-CROP|CROP-AFF-ABS|19|0|5|0|方向较稳定，谨慎删除|
|MRK-LOI-QTL|QTL-LOI-MRK|16|1|8|0|方向较稳定，谨慎删除|
|BIS-AFF-CROP|CROP-AFF-BIS|20|0|3|0|方向较稳定，谨慎删除|
|ABS-AFF-VAR|VAR-AFF-ABS|15|0|3|0|方向较稳定，谨慎删除|
|GENE-HAS-TRT|TRT-HAS-GENE|16|0|2|0|方向较稳定，谨慎删除|
|TRT-CON-TRT|TRT-CON-TRT|17|17|0|0||
|CROSS-HAS-TRT|TRT-HAS-CROSS|14|0|2|0|方向较稳定，谨慎删除|
|GENE-LOI-QTL|QTL-LOI-GENE|15|9|1|1|方向较稳定，谨慎删除|
|MRK-CON-MRK|MRK-CON-MRK|15|15|0|0||
|VAR-CON-VAR|VAR-CON-VAR|12|12|1|1|方向较稳定，谨慎删除|
|CROP-CON-CROSS|CROSS-CON-CROP|11|5|0|0||
|BIS-LOI-QTL|QTL-LOI-BIS|1|7|0|3||
|BM-USE-MRK|MRK-USE-BM|7|3|3|1||
|ABS-CON-ABS|ABS-CON-ABS|9|9|0|0||
|BIS-OCI-GST|GST-OCI-BIS|7|0|2|0||
|BIS-AFF-BIS|BIS-AFF-BIS|5|5|3|3||
|ABS-AFF-QTL|QTL-AFF-ABS|7|0|0|0||
|BM-USE-TRT|TRT-USE-BM|4|4|3|0||
|BM-CON-BM|BM-CON-BM|6|6|0|0||
|GENE-CON-QTL|QTL-CON-GENE|1|5|0|1||

## 2. v44 低频关系与反向证据

|类型|v44数|训练频次|v44反向数|训练反向频次|建议|
|---|---:|---:|---:|---:|---|
|BM-USE-CROSS|1|1|1|3|单类型消融或样本簇消融|
|VAR-OCI-GST|2|1|0|0|单类型消融或样本簇消融|
|QTL-AFF-BIS|3|1|0|0|单类型消融或样本簇消融|
|GENE-CON-TRT|4|1|0|1|单类型消融或样本簇消融|
|BIS-CON-BIS|1|2|1|2|单类型消融或样本簇消融|
|BM-USE-QTL|1|2|0|0|单类型消融或样本簇消融|
|GENE-LOI-CROP|1|2|0|2|单类型消融或样本簇消融|
|BM-AFF-GENE|2|2|0|0|单类型消融或样本簇消融|
|GENE-LOI-MRK|5|2|2|22|方向 QA 优先；先删后换成对提交|
|CROSS-USE-BM|1|3|1|1|人工复核后保守处理|
|CROSS-USE-MRK|1|3|0|0|人工复核后保守处理|
|MRK-USE-BM|1|3|3|7|人工复核后保守处理|
|TRT-AFF-GENE|1|3|86|177|人工复核后保守处理|
|QTL-CON-QTL|1|4|1|4|人工复核后保守处理|
|VAR-CON-GENE|1|4|0|2|人工复核后保守处理|
|BM-USE-TRT|3|4|0|4|暂不整包删除，按样本簇拆分|
|GENE-OCI-GST|1|5|0|0|人工复核后保守处理|
|QTL-CON-GENE|1|5|0|1|人工复核后保守处理|
|BIS-AFF-BIS|3|5|3|5|暂不整包删除，按样本簇拆分|
|TRT-LOI-CHR|3|5|0|0|暂不整包删除，按样本簇拆分|

## 3. 低频样本簇 Top25

|样本idx|类型|条数|关系摘要|实验建议|
|---:|---|---:|---|---|
|372|GENE-CON-TRT|4|AsTCP genes->CON->hormone response ; AsTCP genes->CON->abiotic stress ; AsTCP genes->CON->light response ; AsTCP genes->CON->growth and development|样本簇删除候选|
|269|BM-USE-TRT|3|Integrative breeding->USE->early maturity ; Integrative breeding->USE->high harvest index ; Integrative breeding->USE->water use efficiency|样本簇删除候选|
|207|TRT-LOI-CHR|3|root volume->LOI->chromosome SBI-04 ; root fresh weight->LOI->chromosome SBI-04 ; root dry weight->LOI->chromosome SBI-04|样本簇删除候选|
|103|GENE-LOI-MRK|3|HORVU7Hr1G000320->LOI->SNP7 ; HORVU7Hr1G000040->LOI->SNP7 ; HORVU1Hr1G000010->LOI->SNP1|样本簇删除候选|
|50|QTL-AFF-BIS|3|Resistance loci->AFF->pathotypes from Texas and Puerto Rico ; resistance locus->AFF->pathotypes from Arkansas ; resistance locus->AFF->pathotypes from Georgia|样本簇删除候选|
|276|BIS-AFF-BIS|2|Puccinia striiformis f. sp. tritici (Pst) race V26->AFF->stripe rust infection ; mixed Pst races->AFF->stripe rust infection|样本簇删除候选|
|13|GENE-LOI-MRK|2|lgs gene->LOI->microsatellite markers SB3344 ; lgs gene->LOI->SB3352|样本簇删除候选|
|399|VAR-OCI-GST|1|BTx623->OCI->seed development|单条人工 QA 候选|
|397|GENE-LOI-CROP|1|FeDREB1->LOI->Fagopyrum esculentum|单条人工 QA 候选|
|377|TRT-AFF-GENE|1|Pep1->AFF->pathogenesis-related protein 1 (PR1) gene|单条人工 QA 候选|
|375|GENE-OCI-GST|1|CcCIPK genes->OCI->roots|单条人工 QA 候选|
|339|BIS-AFF-BIS|1|Pyricularia spp.->AFF->Leaf blast disease|单条人工 QA 候选|
|246|MRK-USE-BM|1|SNPs->USE->genotyping-by-sequencing|单条人工 QA 候选|
|209|BM-AFF-GENE|1|MAT->AFF->phytoene desaturase gene|单条人工 QA 候选|
|185|CROSS-USE-BM|1|F-2 mapping population->USE->DArTseq|单条人工 QA 候选|
|179|QTL-CON-GENE|1|qSL2-1->CON->genes|单条人工 QA 候选|
|177|BM-AFF-GENE|1|CRISPR/Cas9->AFF->susceptibility genes|单条人工 QA 候选|
|138|QTL-CON-QTL|1|QTLs->CON->clusters|单条人工 QA 候选|
|136|BM-USE-QTL|1|marker assisted selection->USE->resistance QTL|单条人工 QA 候选|
|80|VAR-OCI-GST|1|Baiyan 2->OCI->three-leaf stage|单条人工 QA 候选|
|64|VAR-CON-GENE|1|sdw1.ZU9->CON->HvGA20ox2|单条人工 QA 候选|
|49|CROSS-USE-MRK|1|F-2 population->USE->RAD-seq|单条人工 QA 候选|
|18|BM-USE-CROSS|1|RAD-seq analysis->USE->F-2 progeny|单条人工 QA 候选|
|2|BIS-CON-BIS|1|southern root-knot nematodes->CON->RKN|单条人工 QA 候选|

## 4. v44 中跨版本稳定性最低的关系 Top30

|出现版本数|样本idx|类型|关系|建议|
|---:|---:|---|---|---|
|4|13|GENE-LOI-MRK|lgs gene->LOI->SB3352|若低频/方向异常则优先复核；否则仅作为观察项|
|4|13|GENE-LOI-MRK|lgs gene->LOI->microsatellite markers SB3344|若低频/方向异常则优先复核；否则仅作为观察项|
|4|103|GENE-LOI-MRK|HORVU1Hr1G000010->LOI->SNP1|若低频/方向异常则优先复核；否则仅作为观察项|
|4|103|GENE-LOI-MRK|HORVU7Hr1G000040->LOI->SNP7|若低频/方向异常则优先复核；否则仅作为观察项|
|4|103|GENE-LOI-MRK|HORVU7Hr1G000320->LOI->SNP7|若低频/方向异常则优先复核；否则仅作为观察项|
|5|2|BIS-CON-BIS|southern root-knot nematodes->CON->RKN|若低频/方向异常则优先复核；否则仅作为观察项|
|5|50|QTL-AFF-BIS|Resistance loci->AFF->pathotypes from Texas and Puerto Rico|若低频/方向异常则优先复核；否则仅作为观察项|
|5|50|QTL-AFF-BIS|resistance locus->AFF->pathotypes from Arkansas|若低频/方向异常则优先复核；否则仅作为观察项|
|5|50|QTL-AFF-BIS|resistance locus->AFF->pathotypes from Georgia|若低频/方向异常则优先复核；否则仅作为观察项|
|5|80|VAR-OCI-GST|Baiyan 2->OCI->three-leaf stage|若低频/方向异常则优先复核；否则仅作为观察项|
|5|177|BM-AFF-GENE|CRISPR/Cas9->AFF->susceptibility genes|若低频/方向异常则优先复核；否则仅作为观察项|
|5|209|BM-AFF-GENE|MAT->AFF->phytoene desaturase gene|若低频/方向异常则优先复核；否则仅作为观察项|
|5|372|GENE-CON-TRT|AsTCP genes->CON->abiotic stress|若低频/方向异常则优先复核；否则仅作为观察项|
|5|372|GENE-CON-TRT|AsTCP genes->CON->growth and development|若低频/方向异常则优先复核；否则仅作为观察项|
|5|372|GENE-CON-TRT|AsTCP genes->CON->hormone response|若低频/方向异常则优先复核；否则仅作为观察项|
|5|372|GENE-CON-TRT|AsTCP genes->CON->light response|若低频/方向异常则优先复核；否则仅作为观察项|
|5|397|GENE-LOI-CROP|FeDREB1->LOI->Fagopyrum esculentum|若低频/方向异常则优先复核；否则仅作为观察项|
|5|399|VAR-OCI-GST|BTx623->OCI->seed development|若低频/方向异常则优先复核；否则仅作为观察项|
|6|0|ABS-AFF-TRT|LN->AFF->primary and lateral root growth|若低频/方向异常则优先复核；否则仅作为观察项|
|6|0|CROP-CON-VAR|Tartary buckwheat->CON->LN-insensitive genotype|若低频/方向异常则优先复核；否则仅作为观察项|
|6|0|CROP-CON-VAR|Tartary buckwheat->CON->LN-sensitive genotype|若低频/方向异常则优先复核；否则仅作为观察项|
|6|0|CROP-CON-VAR|Tartary buckwheat->CON->genotypes|若低频/方向异常则优先复核；否则仅作为观察项|
|6|0|VAR-HAS-TRT|LN-sensitive genotype->HAS->primary and lateral root growth|若低频/方向异常则优先复核；否则仅作为观察项|
|6|1|TRT-OCI-GST|Seed set->OCI->early generations|若低频/方向异常则优先复核；否则仅作为观察项|
|6|1|VAR-HAS-TRT|Autotetraploid sorghum inbreds->HAS->kernel weight|若低频/方向异常则优先复核；否则仅作为观察项|
|6|1|VAR-HAS-TRT|Autotetraploid sorghum inbreds->HAS->protein and amino acid content|若低频/方向异常则优先复核；否则仅作为观察项|
|6|1|VAR-HAS-TRT|Autotetraploid sorghum inbreds->HAS->seed yield|若低频/方向异常则优先复核；否则仅作为观察项|
|6|1|VAR-HAS-TRT|autotetraploids->HAS->Seed set|若低频/方向异常则优先复核；否则仅作为观察项|
|6|1|VAR-HAS-TRT|autotetraploids->HAS->Stalk height|若低频/方向异常则优先复核；否则仅作为观察项|
|6|1|VAR-HAS-TRT|autotetraploids->HAS->panicle length|若低频/方向异常则优先复核；否则仅作为观察项|

## 5. v46/v47 原子实验队列

|优先级|实验名|学术依据|修改对象|提交纪律|
|---:|---|---|---|---|
|1|`v46_direction_gene_loi_mrk_delete_vs_swap`|Directionality + Entity-role QA|5 条 GENE-LOI-MRK 与 5 条 MRK-LOI-GENE 对照|先删后换，必须成对解释|
|2|`v46_lowfreq_gene_con_trt_cluster372`|Data-centric FP cleaning|样本 372 的 4 条 GENE-CON-TRT|只删一个样本簇|
|3|`v46_lowfreq_qtl_aff_bis_cluster50`|Data-centric FP cleaning|样本 50 的 3 条 QTL-AFF-BIS|只删一个样本簇|
|4|`v46_llmqa_review_lowfreq_top20`|QA + entity type markers|训练频次<=2且v44存在的关系|离线判别，不直接提交|
|5|`v47_external_biorex_pubtator_evidence`|Weak supervision + external evidence|基因/标记/性状类关系外部证据|只做证据排序|
|6|`v47_stability_forgetting_subtract`|Noisy label forgetting proxy|跨版本不稳定且低频关系|每次删除<=5条|
|7|`v47_abs_aff_gene_micro_add`|唯一历史有效加法的同源扩展|ABS-AFF-GENE 候选|每次新增<=3条且需 QA 证据|
