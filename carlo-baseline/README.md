# flf-epistack-contest — COVID-origins baseline

A quick baseline for the [FLF Epistemic Case Study Competition](https://www.lesswrong.com/posts/frizRHnA6AZpJSDqw/lab-leaks-black-holes-and-eggs-epistemic-case-study) (COVID-19 origins case study).

I ran a **23-minute Claude Code swarm** on the COVID-origins question, using **Claude Opus 4.8**, to use as a baseline — a sense of how far a single unattended agent run gets before adding any bespoke epistemic tooling. It produced **40 sourced evidence documents** drawing on **192 unique sources**, and a synthesis calibrated at roughly **72% natural origin / 28% lab-related**.

The whole catalog (this repo's `INDEX.md`, the 40 files in `evidence/`, and `CONCLUSION.md`) was researched and written by **Claude**, not by me. It summarizes public peer-reviewed literature, official reports, and primary documents. It is a reasoned synthesis, not an authoritative scientific verdict.

## The prompt

The entire run came from a single prompt:

> work in the folder AI/flf/covid. research the topic of the origin of covid: was it leaked from a lab? was it developed naturally? what are the contested theories? what are the compelling evidences? base your research on broad informations that you can find online, peer reviewed studies, compelling evidences. gather evidences, write a new document for each evidence you find, referencing the original sources, then write for each a summary with the key facts and some confidence score. use workflows and swarms of agents as you see fit. goal there are as many sources collected and catalogated as possible, and a final summary document with the conclusion, epistemically valid

## What's here

- **[`INDEX.md`](INDEX.md)** — the evidence catalog: all 40 items sorted by side (natural / lab / shared confound) and by support strength.
- **[`CONCLUSION.md`](CONCLUSION.md)** — the synthesis, the two hypotheses stated precisely, and how the evidence is weighed into the ~72/28 estimate.
- **[`evidence/`](evidence/)** — one file per piece of evidence. Each states a single claim, its key facts, the strongest counterargument, sourced references, and two calibrated scores:
  - **claim_confidence (0–1)** — how likely the underlying factual claim is true.
  - **support_strength (weak / moderate / strong)** — how much the true fact actually moves the origin question.

The two scores are kept separate on purpose: a high-confidence fact can still be weakly probative (e.g. the furin cleavage site is real at ≈0.97, but near-neutral on origin).

## Caveats

This is a *baseline*, not a submission of finished tooling. It's the raw output of one unattended agent run — useful as a floor to measure epistemic-stack techniques against, not as a polished knowledge base. Scores are the model's own calibration and should be read as such.
