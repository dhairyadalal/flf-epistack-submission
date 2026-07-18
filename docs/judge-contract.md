# Future judge contract

The first version contains no LLM judge. This is intentional: a source-class
heuristic is not a source evaluation, and an unverified model opinion must not
silently upgrade an annotation's status.

A future judge should implement one narrow operation:

```text
review(annotation, declared_policy, retrieved_source_content) -> review_record
```

The operation must:

1. receive a specific annotation version and policy version;
2. distinguish metadata checks from full-content checks;
3. quote or locate the evidence supporting each judgment;
4. record unavailable content instead of inferring it;
5. separate source quality, relevance, independence, and claim support;
6. identify framing assumptions and policy sensitivity;
7. attribute uncertainty qualitatively unless a quantitative method is supplied;
8. append a review record rather than mutate the baseline assertion;
9. record model, prompt, parameters, timestamp, and any human confirmation;
10. leave final status as provisional until the configured verification threshold is met.

## Recommended review states

- `not_checked` — citation was only extracted.
- `metadata_checked` — identity, publication, date, and access were checked.
- `content_checked` — relevant source content was inspected.
- `independently_audited` — the full evidence annotation passed the project's
  declared audit procedure, which may require human confirmation.

The reviewer's output should conform to a future versioned JSON Schema. The
browser should render competing reviews side by side rather than collapse them
into a single hidden score.

