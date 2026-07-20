---
title: "The serial-passage / cell-culture adaptation hypothesis — and why the intact furin site in early isolates argues against it"
slug: serial-passage-cell-culture-adaptation
direction: lab-leak
evidence_type: virological
claim_confidence: 0.4
support_strength: weak
author: Claude
date: 2026-06-25
---

# The serial-passage / cell-culture adaptation hypothesis

> Written by Claude (not by Carlo). One item in the COVID-origins evidence catalog.

## Claim
A lab-origin variant holds that a natural bat sarbecovirus, repeatedly grown ("serially passaged") in cell culture or in humanized/animal models, could have acquired human-adapted features — including, on some versions, the furin cleavage site (FCS) — and then leaked, leaving **no engineering signature** in the genome (the "no-see-um" scenario). This document assesses that specific mechanistic claim, not the broader lab-leak question.

## Key facts
- The hypothesis is attractive to lab-origin proponents precisely because it predicts **no detectable manipulation**: passage-driven adaptation looks "natural" at the sequence level, so the absence of cloning scars (raised in `furin-cleavage-site-prra-insertion`) would not refute it.
- It runs into a strong, reproducible empirical fact pointing the **other way**: when SARS-CoV-2 is grown in the standard Vero E6 cell line, it **loses** the furin cleavage site by in-frame deletion within a few passages (Davidson et al. 2020, *Genome Medicine*; Ogando et al. 2020; Klimstra et al. 2020). Vero cells express TMPRSS2 poorly, so the FCS is not under positive selection and is rapidly deleted.
- Retaining the FCS in culture requires deliberately using **TMPRSS2-expressing airway lines such as Calu-3** (Mautner et al. 2022, *Virology Journal*, PMC8704555). So a passage history would have to be specifically engineered to *preserve* the FCS — which is closer to purposeful selection than to incidental adaptation.
- The decisive observation: the **earliest sampled human isolates (Dec 2019–Jan 2020) carry an intact, fully functional FCS** with no culture-adaptation deletions or the tissue-culture marker mutations (e.g. spike R682 changes) that passage reliably produces. If the virus had emerged *from* extended cell culture, early isolates should bear those scars; they do not (Andersen et al. 2020, *Nature Medicine*; Holmes et al. 2021, *Cell*).
- Andersen et al. also note that the SARS-CoV-2 RBD bound human ACE2 by a solution **not predicted** by the structural models then used to design optimized binders, which argues against both deliberate engineering and against optimization through cell-culture selection in a non-physiological system (see companion doc `rbd-not-optimal-for-human-ace2`).

## Evidence quality
The data underpinning the **rebuttal** are strong and independently replicated: multiple labs worldwide documented FCS loss on Vero passage in peer-reviewed journals, and the intactness of the FCS in early isolates is directly observable in public genome databases. The **hypothesis itself** is largely a logical possibility argument with no positive supporting data — no documented passage series at any lab has been shown to produce SARS-CoV-2 or a near-progenitor. It is unfalsifiable in its strongest "no-see-um" form, which is an epistemic weakness, not a strength.

## Strongest counterargument
Proponents respond that passage in a humanized-mouse model or a TMPRSS2-positive human airway line (not Vero) could plausibly **maintain** the FCS while adapting the RBD, and that we cannot exclude such an experiment because WIV's full culture and animal-model records are not public (`china-data-withholding-transparency`). This is true but cuts against itself: it converts the hypothesis into an unfalsifiable claim resting on the *absence* of records rather than any positive evidence, and the specific, repeatedly observed behavior of the virus (FCS lost under ordinary passage) still has to be argued around rather than explained.

## Confidence assessment
- **Claim confidence:** 0.4 — As a bare *possibility* the mechanism is real (viruses do adapt in culture); as an *explanation for SARS-CoV-2 specifically* it is unsupported by any positive evidence and is in tension with the intact-FCS-in-early-isolates fact. I assign low-moderate confidence that the claim (passage explains SARS-CoV-2's features) is true.
- **Support strength:** weak — Even if one grants the mechanism is conceivable, it provides no discriminating evidence for a lab origin; it is a way to *reconcile* lab origin with the lack of an engineering signature, not evidence *for* it.
- **Net:** A calibrated reasoner should treat the serial-passage idea as an unfalsifiable escape hatch with no positive support and some contrary empirical evidence (FCS deletes under normal passage; early isolates are unscarred), not as affirmative evidence of a lab origin.

## Sources
1. Andersen, K.G., Rambaut, A., Lipkin, W.I., Holmes, E.C., Garry, R.F. (2020). The proximal origin of SARS-CoV-2. *Nature Medicine* 26, 450–452. https://www.nature.com/articles/s41591-020-0820-9
2. Davidson, A.D. et al. (2020). Characterisation of the transcriptome and proteome of SARS-CoV-2 reveals a cell passage induced in-frame deletion of the furin-like cleavage site from the spike glycoprotein. *Genome Medicine* 12, 68. https://genomemedicine.biomedcentral.com/articles/10.1186/s13073-020-00763-0
3. Mautner, L. et al. (2022). Propagation of SARS-CoV-2 in Calu-3 Cells to Eliminate Mutations in the Furin Cleavage Site of Spike. PMC8704555. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8704555/
4. Holmes, E.C. et al. (2021). The origins of SARS-CoV-2: A critical review. *Cell* 184, 4848–4856. https://doi.org/10.1016/j.cell.2021.08.017
