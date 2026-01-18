# The Umeton Index: A Binary Author-Position Filter for Measuring Research Leadership Impact

**Renato Umeton**

Office of Data Science, St. Jude Children's Research Hospital, Memphis, TN, USA

Email: renato.umeton@stjude.org

---

## Abstract

The h-index, while widely adopted for evaluating scientific impact, treats all co-authorships equally regardless of an author's role in the research. This creates distortions in fields where authorship conventions assign meaning to author position. We propose the Umeton index (U-index), a modification of the h-index that counts only publications where the researcher occupies a first or last author position. Formally, a researcher has Umeton index U if U of their first-or-last-authored papers have each received at least U citations. Unlike weighted approaches that assign fractional credit, the U-index employs a binary filter: a paper either counts toward the index or it does not. This simplicity makes the metric transparent, easily calculable, and resistant to inflation through accumulation of middle-author positions on collaborative works. We discuss the theoretical properties of the U-index, its relationship to existing author-position-aware metrics, and its limitations in fields without strong authorship position conventions.

**Keywords:** bibliometrics, h-index, authorship, citation metrics, research evaluation, scientific impact

---

## 1. Introduction

Since its introduction by Hirsch in 2005 [1], the h-index has become one of the most widely used metrics for evaluating individual scientific output. Its elegant definition---a researcher has index h if h of their papers have each been cited at least h times---balances productivity and impact in a single number. However, the h-index has well-documented limitations [2,3], chief among them its insensitivity to author position and the number of co-authors on a publication.

In many scientific fields, particularly in the biomedical and life sciences, authorship position carries significant meaning. First authorship typically indicates the person who conducted the primary research work, while last authorship generally denotes the senior scientist who supervised the project, secured funding, and provided intellectual leadership [4,5]. Middle authorship positions, by contrast, often reflect supporting contributions of varying magnitude. The standard h-index makes no distinction among these roles, granting equal credit to all authors regardless of their contribution.

This creates perverse incentives. A researcher can inflate their h-index by accumulating middle-author positions on large consortium papers or collaborative works without ever leading independent research. This phenomenon has been documented across multiple fields and has prompted calls for author-position-aware metrics [4,6,7].

Several approaches have been proposed to address this limitation. The Schreiber hm-index uses fractional counting based on the number of co-authors [8]. The Stanford/Ioannidis composite c-score incorporates citations to single, first, and last author positions into a multi-indicator framework [6,7]. The c-index family developed by Post et al. characterizes the h-core by author position [4]. Most recently, the h-leadership index by Jain and Chandra uses a Gaussian-weighted scheme that assigns higher credit to first and last positions [9].

Here we propose a fundamentally simpler approach: the Umeton index (U-index), which applies a binary filter to the h-index calculation, counting only papers where the researcher is either first or last author. This approach prioritizes transparency and interpretability over nuance, providing a clear answer to a specific question: how many impactful works has this researcher led or supervised?

---

## 2. Definition

Let P denote the complete set of publications authored by researcher R. We define the **leadership subset** L(R) as:

$$L(R) = \{p \in P : R \text{ is first author of } p \text{ OR } R \text{ is last author of } p\}$$

The **Umeton index** U is then defined as:

$$U = \max\{u \in \mathbb{Z}^+ : |\{p \in L(R) : c(p) \geq u\}| \geq u\}$$

where c(p) denotes the citation count of paper p.

In plain language: **A researcher has Umeton index U if U of their first-or-last-authored papers have each been cited at least U times.**

### 2.1 Handling Edge Cases

**Single-author papers:** A single-author paper qualifies the author as first author; such papers are included in L(R).

**Corresponding authorship:** Corresponding author status does not qualify, as practices vary substantially across fields and journals.

**Co-first and co-last authorship:** These designations are intentionally not taken into consideration. They are impossible to distinguish from the problematic incentive structure that this index aims to address. The U-index is designed to be simple and strict.

---

## 3. Properties

### 3.1 Boundedness

The Umeton index is bounded above by the standard h-index:

$$U \leq h$$

This follows directly from the fact that L(R) is a subset of P. The U-index can never exceed h because it considers only a subset of the papers used to calculate h.

### 3.2 Monotonicity

If a researcher publishes an additional first-or-last-authored paper, U can only increase or stay the same. Formally, for any researcher R with index U, adding a paper p where R is first or last author yields U' >= U.

### 3.3 Robustness to Middle Authorship Inflation

By construction, U is completely insensitive to the accumulation of middle-author positions. A researcher who publishes 100 papers as middle author on highly-cited consortium studies will see their h-index rise substantially, but their U-index will remain unchanged.

### 3.4 Career Stage Dynamics

The U-index exhibits characteristic patterns across career stages in fields with traditional authorship conventions:

- **Early career:** Researchers typically accumulate first-author papers, building U through primary research contributions.
- **Mid career:** A mix of first-author papers (independent work) and last-author papers (supervised work) contribute to U.
- **Senior career:** Last-author papers dominate as researchers supervise trainees and lead laboratories.

This provides richer interpretive information than the standard h-index, which conflates these distinct contribution types.

---

## 4. Relationship to Existing Metrics

### 4.1 Comparison with the Stanford c-score

The Stanford/Ioannidis approach [6,7] tracks citations to papers in three author position categories: single author (NCS), single or first author (NCSF), and single, first, or last author (NCSFL). These are combined with total citations (NC), h-index (H), and co-authorship-adjusted hm-index (Hm) into a composite indicator via log transformation and standardization.

The U-index differs in two key respects: (1) it modifies which papers count toward an h-like calculation rather than tracking citation statistics, and (2) it produces a single interpretable number rather than a composite score.

### 4.2 Comparison with the c-index Family

Post et al. [4] introduced indices hp (first/second author count in h-core), hs (last/second-to-last author count), and hi (internal author count), along with weighted variants cp, cs, and co. These characterize the composition of the h-core by author position.

The U-index is more restrictive: it excludes second and second-to-last positions, and it computes a filtered h-index rather than characterizing the standard h-core.

### 4.3 Comparison with the h-leadership Index

Jain and Chandra [9] assign weights to all author positions using a modified complementary Gaussian curve, with first and last positions receiving weight 1.0 and middle positions receiving progressively lower weights down to a floor of 0.3. Citations are weighted accordingly before computing an h-like index.

The U-index takes the limiting case of this approach: first/last positions receive weight 1, all other positions receive weight 0. This binary approach sacrifices granularity for simplicity and interpretability.

### 4.4 Comparison with the hm-index

Schreiber's hm-index [8] uses fractional counting: each paper contributes 1/k to the effective paper count, where k is the number of co-authors. This addresses multi-authorship but is position-blind.

The U-index is author-count-agnostic but position-sensitive---the opposite trade-off.

---

## 5. Limitations

### 5.1 Field Dependence

The U-index assumes that first and last author positions carry meaning. This assumption holds strongly in biomedical and life sciences, clinical medicine, and many areas of experimental sciences.

However, the assumption fails in fields with different conventions:

- **Mathematics:** Alphabetical author ordering is common.
- **Theoretical physics:** Alphabetical ordering is also frequent.
- **Economics:** Alphabetical ordering predominates.
- **Large collaborations (particle physics, astronomy):** Author lists may be strictly alphabetical or follow consortium conventions.

In such fields, the U-index is not meaningful and should not be applied.

### 5.2 Hyperauthorship

In papers with hundreds of authors (common in particle physics, genomics consortia, and large clinical trials), distinguishing meaningful first/last authorship becomes problematic. Many such papers have consortium authorship with individuals listed alphabetically or by institutional contribution. The U-index may inadvertently credit authors who happen to fall at list boundaries due to alphabetical ordering.

### 5.3 Evolving Authorship Norms

Some fields are moving toward contribution-based authorship statements (e.g., CRediT taxonomy) that explicitly enumerate each author's role. As these practices mature, they may provide better foundations for contribution-aware metrics than author position alone.

### 5.4 Small Group Bias

Solo-authored papers automatically place the author in a qualifying position, and two-author papers qualify both authors (one as first, one as last). This may modestly favor researchers who publish primarily with small teams, though the effect is likely small in practice given that both the paper count and citation threshold must be satisfied.

---

## 6. Discussion

The Umeton index provides a deliberately simple answer to a specific question: how much impactful research has this person led or supervised? Its binary nature---a paper counts or it does not---eliminates ambiguity and makes the metric trivially verifiable.

We do not propose the U-index as a replacement for the h-index or other metrics. Rather, it serves as a complement that isolates leadership contributions. Consider two researchers with identical h-indices of 30:

- **Researcher A:** U = 25 (most h-core papers are first/last authored)
- **Researcher B:** U = 8 (most h-core papers are middle-authored)

These researchers have markedly different publication profiles that the standard h-index obscures. Researcher A has demonstrated sustained independent research leadership; Researcher B has built their h-index primarily through collaborative contributions.

Neither profile is inherently better---science requires both leaders and collaborators---but the distinction matters for certain evaluative contexts, such as assessing readiness for independent positions or research group leadership.

### 6.1 Practical Calculation

The U-index can be calculated from any bibliometric database that records author order:

1. Retrieve all publications for researcher R
2. Filter to papers where R is first or last author
3. Sort by citation count (descending)
4. Find the largest u where paper u has at least u citations

This procedure is implementable in Scopus, Web of Science, Google Scholar (with manual verification), and Dimensions.

### 6.2 Recommended Use

We recommend reporting the U-index alongside, not instead of, the standard h-index. The pair (h, U) provides more information than either alone:

- h >> U: Impact built primarily through collaborative contributions
- h approximately equal to U: Impact concentrated in leadership positions
- U approaching h: Strong independent research profile

Additionally, users may wish to decompose U into its first-author and last-author components (U_F and U_L) for finer-grained analysis, though we leave this extension to future work.

---

## 7. Conclusion

The Umeton index offers a minimal, transparent modification to the h-index that isolates research leadership contributions. By counting only first-or-last-authored papers, it provides a metric resistant to inflation through middle authorship while remaining simple to calculate and interpret.

The U-index is not appropriate for all fields or all evaluative purposes. It assumes authorship position conventions that do not hold universally, and it deliberately ignores collaborative contributions that may be scientifically valuable. However, for fields where first and last authorship denote meaningful leadership roles, the U-index provides a useful complement to existing metrics.

We release this metric into the public domain and encourage its evaluation across diverse scientific communities.

---

## References

[1] Hirsch, J.E. (2005). An index to quantify an individual's scientific research output. *Proceedings of the National Academy of Sciences*, 102(46), 16569-16572. https://doi.org/10.1073/pnas.0507655102

[2] Bornmann, L., & Daniel, H.-D. (2007). What do we know about the h index? *Journal of the American Society for Information Science and Technology*, 58(9), 1381-1385. https://doi.org/10.1002/asi.20609

[3] Waltman, L., & van Eck, N.J. (2012). The inconsistency of the h-index. *Journal of the American Society for Information Science and Technology*, 63(2), 406-415. https://doi.org/10.1002/asi.21678

[4] Post, A., Li, A.Y., Dai, J.B., Maniya, A.Y., Haider, S., Sobotka, S., & Choudhri, T.F. (2018). c-index and Subindices of the h-index: New Variants of the h-index to Account for Variations in Author Contribution. *Cureus*, 10(5), e2629. https://doi.org/10.7759/cureus.2629

[5] Wren, J.D., Kozak, K.Z., Johnson, K.R., Deakyne, S.J., Schilling, L.M., & Dellavalle, R.P. (2007). The write position: A survey of perceived contributions to papers based on byline position and number of authors. *EMBO Reports*, 8(11), 988-991. https://doi.org/10.1038/sj.embor.7401095

[6] Ioannidis, J.P.A., Klavans, R., & Boyack, K.W. (2016). Multiple Citation Indicators and Their Composite across Scientific Disciplines. *PLoS Biology*, 14(7), e1002501. https://doi.org/10.1371/journal.pbio.1002501

[7] Ioannidis, J.P.A., Baas, J., Klavans, R., & Boyack, K.W. (2019). A standardized citation metrics author database annotated for scientific field. *PLoS Biology*, 17(8), e3000384. https://doi.org/10.1371/journal.pbio.3000384

[8] Schreiber, M. (2008). To share the fame in a fair way, hm modifies h for multi-authored manuscripts. *New Journal of Physics*, 10, 040201. https://doi.org/10.1088/1367-2630/10/4/040201

[9] Jain, H.A., & Chandra, R. (2025). Research impact evaluation based on effective authorship contribution sensitivity: h-leadership index. *arXiv*:2503.18236. https://arxiv.org/abs/2503.18236

---

## Acknowledgments

The author thanks the Office of Data Science at St. Jude Children's Research Hospital for support.

## Competing Interests

The author declares no competing interests.

## Data Availability

No datasets were generated or analyzed in this study. The proposed metric can be calculated from publicly available bibliometric databases.
