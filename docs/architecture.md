# Architecture

## Principle

Raw inputs, model-authored assertions, our annotations, and UI projections are
different artifacts. They must remain distinguishable at every stage.

## Data flow

1. Baseline Markdown is treated as immutable input.
2. The Python parser extracts its declared claims, scores, prose assessments,
   and citations without changing them.
3. Broad citation classes are added with an explicitly named heuristic.
4. Canonical JSON annotation records are emitted under `data/annotations/`.
5. A compact browser projection is emitted to `site/data/catalog.json`.
6. Fixed-corpus experiment specifications group dependent evidence, declare
   policy filters, and generate assessment diffs without recollecting sources.
7. The static site renders the projection and never performs epistemic analysis.

## COVID ablation

The COVID experiment keeps the imported corpus immutable. Three nested policies
select subsets of the same 40 records. The build groups records into declared
independence clusters, takes at most one maximum support contribution per cluster
and direction, and emits the result with a prominent non-probability caveat.

The graph has explicit claim, warrant, hypothesis, and independence-cluster
nodes. A warrant is the annotated inferential assumption connecting a baseline
claim to an origin hypothesis; it is not treated as another factual observation.

## Trust boundary

`extracted_not_verified` means exactly that. A future judge—human, LLM, or
hybrid—must create a new review layer and advance the status only when it has
checked the relevant metadata or content. It must not overwrite upstream prose.

## Why no backend

GitHub Pages cannot run Python. Keeping analysis offline and publishing only
versioned JSON makes the demonstration reproducible, cheap to host, and easy to
inspect. A future API may invoke the same package without changing the artifact
contracts.
