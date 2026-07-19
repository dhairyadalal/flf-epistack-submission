const state = {
  catalog: null,
  caseIndex: 0,
  selectedId: null,
  query: "",
  direction: "all",
  runIndex: 0,
  clusterId: null,
};

const elements = {
  tabs: document.querySelector("#case-tabs"),
  kicker: document.querySelector("#case-kicker"),
  title: document.querySelector("#case-title"),
  description: document.querySelector("#case-description"),
  boundary: document.querySelector("#review-boundary"),
  metrics: document.querySelector("#metrics"),
  experimentSection: document.querySelector("#experiment-section"),
  experimentKicker: document.querySelector("#experiment-kicker"),
  experimentTitle: document.querySelector("#experiment-title"),
  experimentDescription: document.querySelector("#experiment-description"),
  runPickerTitle: document.querySelector("#run-picker-title"),
  runPickerDescription: document.querySelector("#run-picker-description"),
  runTabs: document.querySelector("#run-tabs"),
  runPanel: document.querySelector("#run-panel"),
  runTitle: document.querySelector("#run-title"),
  runDescription: document.querySelector("#run-description"),
  runCounts: document.querySelector("#run-counts"),
  assessmentLabel: document.querySelector("#assessment-label"),
  assessmentConclusion: document.querySelector("#assessment-conclusion"),
  naturalBalance: document.querySelector("#natural-balance"),
  researchBalance: document.querySelector("#research-balance"),
  naturalBar: document.querySelector("#natural-bar"),
  researchBar: document.querySelector("#research-bar"),
  supportBalance: document.querySelector("#support-balance"),
  framingOutput: document.querySelector("#framing-output"),
  answerShape: document.querySelector("#answer-shape"),
  graphTitle: document.querySelector("#graph-title"),
  graphDescription: document.querySelector("#graph-description"),
  graphFilterField: document.querySelector("#graph-filter-field"),
  graphLegend: document.querySelector("#graph-legend"),
  clusterFilter: document.querySelector("#cluster-filter"),
  graph: document.querySelector("#claim-graph"),
  graphSummary: document.querySelector("#graph-summary"),
  graphSelection: document.querySelector("#graph-selection"),
  coverage: document.querySelector("#coverage-report"),
  coverageSummary: document.querySelector("#coverage-summary"),
  coverageDetails: document.querySelector("#coverage-details"),
  framingSidebar: document.querySelector("#framing-sidebar"),
  framingSidebarTitle: document.querySelector("#framing-sidebar-title"),
  framingMode: document.querySelector("#framing-mode"),
  framingQuestion: document.querySelector("#framing-question"),
  framingSources: document.querySelector("#framing-sources"),
  framingPolicyExclusions: document.querySelector("#framing-policy-exclusions"),
  framingExclusions: document.querySelector("#framing-exclusions"),
  framingConsequence: document.querySelector("#framing-consequence"),
  resultCount: document.querySelector("#result-count"),
  search: document.querySelector("#search"),
  direction: document.querySelector("#direction-filter"),
  directionLabel: document.querySelector("#direction-label"),
  list: document.querySelector("#evidence-list"),
  detail: document.querySelector("#evidence-detail"),
  policySection: document.querySelector("#policy-section"),
  policyDescription: document.querySelector("#policy-description"),
  policies: document.querySelector("#policy-grid"),
};

function el(tag, options = {}, children = []) {
  const node = document.createElement(tag);
  if (options.className) node.className = options.className;
  if (options.text !== undefined) node.textContent = options.text;
  for (const [name, value] of Object.entries(options.attrs || {})) {
    node.setAttribute(name, value);
  }
  for (const child of Array.isArray(children) ? children : [children]) {
    if (child) node.append(child);
  }
  return node;
}

function currentCase() {
  return state.catalog.cases[state.caseIndex];
}

function currentExperiment() {
  const caseId = currentCase().manifest.case_id;
  return state.catalog.experiments.find((experiment) => experiment.case_id === caseId) || null;
}

function label(value) {
  return value.replaceAll("-", " ").replaceAll("_", " ");
}

function renderTabs() {
  elements.tabs.replaceChildren();
  state.catalog.cases.forEach((caseData, index) => {
    const caseId = caseData.manifest.case_id;
    const button = el("button", {
      text: caseId === "covid-origins" ? "COVID origins" : "Eggs",
      attrs: {
        type: "button",
        role: "tab",
        "aria-selected": String(index === state.caseIndex),
      },
    });
    button.addEventListener("click", () => {
      state.caseIndex = index;
      state.selectedId = null;
      state.query = "";
      state.direction = "all";
      state.runIndex = 0;
      state.clusterId = null;
      elements.search.value = "";
      render();
    });
    elements.tabs.append(button);
  });
}

function renderCaseHeader(caseData) {
  const isCovid = caseData.manifest.case_id === "covid-origins";
  const reusedSources = caseData.sources.filter((source) => source.occurrences.length > 1).length;
  const experiment = currentExperiment();

  if (isCovid) {
    elements.kicker.textContent = "Imported baseline · structural review";
    elements.title.textContent = "COVID-origins evidence review";
    elements.description.textContent =
      "Forty supplied evidence notes, reviewed for framing assumptions, missing evidence, and dependencies between claims.";
    elements.boundary.replaceChildren(
      el("strong", { text: "Review boundary" }),
      el("span", {
        text: "We reviewed every supplied evidence note. We did not independently read and verify all 173 cited source documents; their source-text status remains not checked.",
      }),
    );
    elements.directionLabel.textContent = "Position";
  } else {
    elements.kicker.textContent = "Original demonstration · framing comparison";
    elements.title.textContent = "What does “good to eat” mean?";
    elements.description.textContent =
      "Four explicit interpretations of the same question produce different evidence requirements.";
    elements.boundary.replaceChildren(
      el("strong", { text: "Scope note" }),
      el("span", {
        text: "This is a small demonstration corpus, not an exhaustive assessment of eggs. Its purpose is to expose how the question changes before sources are selected.",
      }),
    );
    elements.directionLabel.textContent = "Framing";
  }

  const metrics = [
    [caseData.manifest.evidence_count, "evidence records"],
    [caseData.manifest.unique_source_count, "unique cited sources"],
    [
      experiment
        ? experiment.experiment_type === "fixed_corpus_ablation"
          ? experiment.clusters.length
          : experiment.runs.filter((run) => run.framing_declared).length
        : reusedSources,
      experiment
        ? experiment.experiment_type === "fixed_corpus_ablation"
          ? "independence clusters"
          : "declared framings"
        : "sources used by multiple records",
    ],
  ];
  elements.metrics.replaceChildren(
    ...metrics.map(([value, description]) =>
      el("div", { className: "metric" }, [
        el("strong", { text: String(value) }),
        el("span", { text: description }),
      ]),
    ),
  );

  const directions = [...new Set(caseData.evidence.map((item) => item.evidence.direction))].sort();
  elements.direction.replaceChildren(
    el("option", {
      text: isCovid ? "All positions" : "All framings",
      attrs: { value: "all" },
    }),
  );
  for (const direction of directions) {
    elements.direction.append(
      el("option", { text: label(direction), attrs: { value: direction } }),
    );
  }
  elements.direction.value = state.direction;
}

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}, textValue = null) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  if (textValue !== null) node.textContent = textValue;
  return node;
}

function wrapText(value, maxCharacters, maxLines = 3) {
  const words = value.split(/\s+/);
  const lines = [];
  let current = "";
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length <= maxCharacters) {
      current = candidate;
    } else {
      if (current) lines.push(current);
      current = word;
      if (lines.length === maxLines - 1) break;
    }
  }
  if (current && lines.length < maxLines) lines.push(current);
  const consumed = lines.join(" ");
  if (consumed.length < value.length && lines.length) {
    lines[lines.length - 1] = `${lines[lines.length - 1].replace(/[.,;:]?$/, "")}…`;
  }
  return lines;
}

function graphNode({ x, y, width, height, labelText, typeText, className, excluded }) {
  const group = svgEl("g", {
    class: `graph-node ${className}${excluded ? " excluded" : ""}`,
  });
  group.append(svgEl("rect", { x, y, width, height, rx: 4 }));
  group.append(
    svgEl(
      "text",
      { x: x + 12, y: y + 17, class: "node-type" },
      `${typeText}${excluded ? " · excluded" : ""}`,
    ),
  );
  const textNode = svgEl("text", { x: x + 12, y: y + 34 });
  wrapText(labelText, className === "warrant" ? 52 : 37).forEach((line, index) => {
    textNode.append(
      svgEl("tspan", { x: x + 12, dy: index === 0 ? 0 : 14 }, line),
    );
  });
  group.append(textNode);
  return group;
}

function renderClaimGraph(experiment, run, caseData) {
  const cluster =
    experiment.clusters.find((item) => item.cluster_id === state.clusterId) ||
    experiment.clusters[0];
  state.clusterId = cluster.cluster_id;
  elements.clusterFilter.value = cluster.cluster_id;

  const includedIds = new Set(run.included_evidence_ids);
  const nodeMap = new Map(experiment.graph.nodes.map((node) => [node.node_id, node]));
  const claims = cluster.evidence_ids.map((evidenceId) => ({
    claim: nodeMap.get(`claim:${evidenceId}`),
    warrant: nodeMap.get(`warrant:${evidenceId}`),
    included: includedIds.has(evidenceId),
  }));
  const includedCount = claims.filter((item) => item.included).length;
  const height = Math.max(390, claims.length * 98 + 62);
  const svg = svgEl("svg", {
    viewBox: `0 0 1000 ${height}`,
    "aria-hidden": "true",
  });

  svg.append(
    svgEl("text", { x: 22, y: 23, class: "node-type" }, "BASELINE CLAIM"),
    svgEl("text", { x: 365, y: 23, class: "node-type" }, "INFERENTIAL WARRANT"),
    svgEl("text", { x: 805, y: 23, class: "node-type" }, "BEARS ON"),
  );

  const targetPositions = {
    "natural-origin": 58,
    "lab-leak": Math.round(height / 2 - 34),
    neutral: height - 94,
  };
  const hypothesisLabels = {
    "natural-origin": "Natural origin",
    "lab-leak": "Research-related origin",
    neutral: "Underdetermined / process",
  };

  for (const direction of ["natural-origin", "lab-leak", "neutral"]) {
    svg.append(
      graphNode({
        x: 805,
        y: targetPositions[direction],
        width: 172,
        height: 66,
        labelText: hypothesisLabels[direction],
        typeText: "Hypothesis",
        className: `hypothesis ${
          direction === "natural-origin" ? "natural" : direction === "lab-leak" ? "research" : "neutral"
        }`,
        excluded: false,
      }),
    );
  }

  claims.forEach(({ claim, warrant, included }, index) => {
    const y = 46 + index * 98;
    const targetY = targetPositions[claim.direction] + 33;
    const edgeClass = `graph-edge${included ? "" : " excluded"}`;
    svg.insertBefore(
      svgEl("path", {
        d: `M 292 ${y + 35} L 365 ${y + 35}`,
        class: edgeClass,
      }),
      svg.firstChild,
    );
    svg.insertBefore(
      svgEl("path", {
        d: `M 735 ${y + 35} C 770 ${y + 35}, 770 ${targetY}, 805 ${targetY}`,
        class: edgeClass,
      }),
      svg.firstChild,
    );

    const link = svgEl("a", { href: "#records-title" });
    link.append(
      graphNode({
        x: 22,
        y,
        width: 270,
        height: 70,
        labelText: claim.label,
        typeText: `${label(claim.evidence_type)} · ${label(claim.support_strength)}`,
        className: "claim",
        excluded: !included,
      }),
    );
    link.addEventListener("click", () => {
      state.selectedId = claim.evidence_id;
      state.query = "";
      state.direction = "all";
      elements.search.value = "";
      renderEvidenceList(caseData);
    });
    svg.append(link);
    svg.append(
      graphNode({
        x: 365,
        y,
        width: 370,
        height: 70,
        labelText: warrant.label,
        typeText: "Inferential assumption",
        className: "warrant",
        excluded: !included,
      }),
    );
  });

  elements.graph.replaceChildren(svg);
  elements.graphSummary.textContent = `${cluster.label}. ${includedCount} of ${claims.length} records are included under ${run.label}. ${claims.map((item) => `${item.claim.label}, bearing on ${hypothesisLabels[item.claim.direction]}`).join(". ")}.`;
  elements.graphSelection.replaceChildren(
    el("strong", { text: cluster.label }),
    document.createTextNode(
      ` — ${cluster.description} ${includedCount} of ${claims.length} records are admitted by this policy.`,
    ),
  );
}

function renderCoverage(experiment) {
  const groups = [
    ["Known but unavailable", experiment.coverage_report.known_but_unavailable],
    ["Capability limited", experiment.coverage_report.capability_limited],
    ["Not established", experiment.coverage_report.not_established],
  ];
  elements.coverage.replaceChildren(
    ...groups.map(([title, items]) =>
      el("section", {}, [
        el("h4", { text: `${title} (${items.length})` }),
        el(
          "ul",
          {},
          items.map((item) =>
            el("li", {}, [
              el("strong", { text: `${item.label}: ` }),
              document.createTextNode(item.note),
            ]),
          ),
        ),
      ]),
    ),
  );
}

function renderRunTabs(experiment, caseData) {
  const run = experiment.runs[state.runIndex];
  const framingHints = {
    "eggs-silent-baseline": "Leaves “good” undefined",
    "eggs-health-population-declared": "Average cardiovascular risk",
    "eggs-health-individual-declared": "Personal lipid response",
    "eggs-animal-welfare-declared": "Conditions for laying hens",
    "eggs-environment-declared": "Production footprint",
  };
  const selectRun = (index, focus = false) => {
    state.runIndex = index;
    renderExperiment(caseData);
    if (focus) elements.runTabs.querySelectorAll("button")[index]?.focus();
  };
  elements.runTabs.replaceChildren(
    ...experiment.runs.map((candidate, index) => {
      const isFraming = experiment.experiment_type === "framing_comparison";
      const button = el("button", {
        attrs: {
          id: `run-tab-${index}`,
          type: "button",
          role: "tab",
          "aria-selected": String(index === state.runIndex),
          "aria-controls": "run-panel",
          tabindex: index === state.runIndex ? "0" : "-1",
        },
      }, [
        el("strong", { text: candidate.label }),
        el("span", {
          text: isFraming
            ? framingHints[candidate.run_id]
            : candidate.description.split(".")[0],
        }),
      ]);
      button.addEventListener("click", () => selectRun(index));
      button.addEventListener("keydown", (event) => {
        let nextIndex = null;
        if (event.key === "ArrowRight") nextIndex = (index + 1) % experiment.runs.length;
        if (event.key === "ArrowLeft") nextIndex = (index - 1 + experiment.runs.length) % experiment.runs.length;
        if (event.key === "Home") nextIndex = 0;
        if (event.key === "End") nextIndex = experiment.runs.length - 1;
        if (nextIndex === null) return;
        event.preventDefault();
        selectRun(nextIndex, true);
      });
      return button;
    }),
  );
  elements.runPanel.setAttribute("aria-labelledby", `run-tab-${state.runIndex}`);
  return run;
}

function renderFixedCorpusExperiment(caseData, experiment) {
  const run = experiment.runs[state.runIndex];
  elements.experimentKicker.textContent = "Fixed-corpus policy ablation";
  elements.experimentTitle.textContent = "How source policy changes the assessment";
  elements.experimentDescription.textContent =
    "The 40 supplied records stay fixed. Each run admits a different subset, then recalculates support after duplicate evidence families are collapsed.";
  elements.experimentSection.classList.remove("framing-experiment");
  elements.runPickerTitle.textContent = "Choose an evidence pass";
  elements.runPickerDescription.textContent =
    "Each pass widens the source policy. Select one to see which records enter and how the assessment changes.";
  elements.coverageDetails.hidden = false;
  elements.framingSidebar.hidden = true;
  elements.assessmentLabel.textContent = "Assessment under this policy";
  elements.supportBalance.hidden = false;
  elements.framingOutput.hidden = true;
  elements.graphFilterField.hidden = false;
  elements.graphTitle.textContent = "Claim → warrant → hypothesis";
  elements.graphDescription.textContent =
    "Records in the same evidence family are shown together and scored once per direction.";
  elements.coverageSummary.textContent = "Coverage and negative space";
  elements.graphLegend.replaceChildren(
    el("span", {}, [el("i", { className: "legend-mark claim-mark" }), document.createTextNode("Claim")]),
    el("span", {}, [el("i", { className: "legend-mark warrant-mark" }), document.createTextNode("Inferential warrant")]),
    el("span", {}, [el("i", { className: "legend-mark hypothesis-mark" }), document.createTextNode("Hypothesis")]),
    el("span", {}, [el("i", { className: "legend-mark excluded-mark" }), document.createTextNode("Excluded by selected policy")]),
  );

  const evidenceCount = run.included_evidence_ids.length;
  const sourceCount = run.included_source_ids.length;
  const addedCount = run.added_since_previous_run.length;
  elements.runTitle.textContent = run.label;
  elements.runDescription.textContent = run.description;
  elements.runCounts.textContent = `${evidenceCount} records · ${sourceCount} sources · ${addedCount} ${state.runIndex === 0 ? "in starting set" : "added in this pass"}`;
  elements.assessmentConclusion.textContent = run.assessment.conclusion;

  const natural = run.assessment.support_balance["natural-origin"] || 0;
  const research = run.assessment.support_balance["research-related"] || 0;
  elements.naturalBalance.textContent = `Natural ${run.assessment.support_points["natural-origin"]} points`;
  elements.researchBalance.textContent = `Research-related ${run.assessment.support_points["research-related"]} points`;
  elements.naturalBar.style.width = `${natural * 100}%`;
  elements.researchBar.style.width = `${research * 100}%`;

  const priorCluster = state.clusterId;
  elements.clusterFilter.replaceChildren(
    ...experiment.clusters.map((cluster) =>
      el("option", {
        text: `${cluster.label} (${cluster.evidence_ids.length})`,
        attrs: { value: cluster.cluster_id },
      }),
    ),
  );
  state.clusterId = experiment.clusters.some((cluster) => cluster.cluster_id === priorCluster)
    ? priorCluster
    : experiment.clusters[0].cluster_id;
  elements.clusterFilter.value = state.clusterId;
  renderClaimGraph(experiment, run, caseData);
  renderCoverage(experiment);
}

function renderFramingGraph(experiment, run, caseData) {
  const nodeMap = new Map(experiment.graph.nodes.map((node) => [node.node_id, node]));
  const prefix = `run:${run.run_id}`;
  const stages = [
    {
      node: nodeMap.get("question:eggs-good-to-eat"),
      type: "Raw question",
      className: "question",
    },
    {
      node: nodeMap.get(`${prefix}:framing`),
      type: run.framing_declared ? "Declared framing" : "Implicit framing",
      className: `framing${run.framing_declared ? "" : " implicit"}`,
    },
    {
      node: nodeMap.get(`${prefix}:policy`),
      type: "Source policy",
      className: "source-policy",
    },
    {
      node: nodeMap.get(`${prefix}:claim`),
      type: "Admitted evidence",
      className: "claim",
    },
    {
      node: nodeMap.get(`${prefix}:assessment`),
      type: "Assessment",
      className: "assessment",
    },
  ];
  const positions = [22, 244, 466, 688, 910];
  const widths = [190, 190, 190, 190, 244];
  const svg = svgEl("svg", {
    viewBox: "0 0 1180 220",
    "aria-hidden": "true",
  });

  for (let index = 0; index < stages.length - 1; index += 1) {
    svg.append(
      svgEl("path", {
        d: `M ${positions[index] + widths[index]} 116 L ${positions[index + 1]} 116`,
        class: "graph-edge",
      }),
    );
    svg.append(
      svgEl("text", {
        x: positions[index] + widths[index] + 8,
        y: 105,
        class: "edge-label",
      }, ["interpreted as", "sets scope", "admits", "shapes"][index]),
    );
  }

  stages.forEach((stage, index) => {
    const node = graphNode({
      x: positions[index],
      y: 74,
      width: widths[index],
      height: 84,
      labelText: stage.node.label,
      typeText: stage.type,
      className: stage.className,
      excluded: false,
    });
    if (stage.node.node_type === "claim") {
      const link = svgEl("a", { href: "#records-title" });
      link.append(node);
      link.addEventListener("click", () => {
        state.selectedId = stage.node.evidence_id;
        state.query = "";
        state.direction = "all";
        elements.search.value = "";
        renderEvidenceList(caseData);
      });
      svg.append(link);
    } else {
      svg.append(node);
    }
  });

  elements.graph.replaceChildren(svg);
  elements.graphSummary.textContent = `${run.label}. The raw question is interpreted as ${run.operationalized_question}. That framing admits ${run.source_scope.source_types.join(", ")} and produces this assessment: ${run.assessment_summary}`;
  elements.graphSelection.replaceChildren(
    el("strong", { text: run.operationalized_question }),
    document.createTextNode(` — ${run.answer_shape}`),
  );
}

function renderFramingCoverage(run) {
  elements.framingSidebarTitle.textContent = run.label;
  elements.framingMode.textContent = run.framing_declared
    ? "Declared choice — selected explicitly before evidence is assessed."
    : "Implicit assumption — the system chose this meaning without asking.";
  elements.framingQuestion.textContent = run.operationalized_question;
  elements.framingSources.replaceChildren(
    ...run.source_scope.source_types.map((sourceType) => el("li", { text: sourceType })),
  );
  elements.framingPolicyExclusions.replaceChildren(
    ...run.source_scope.exclusion_rules.map((rule) => el("li", { text: rule })),
  );
  elements.framingExclusions.replaceChildren(
    ...run.excluded_by_framing.map((item) =>
      el("li", {}, [
        el("strong", { text: label(item.framing_id) }),
        document.createTextNode(` — ${item.title}`),
      ]),
    ),
  );
  elements.framingConsequence.textContent = run.framing_conditional_uncertainty;
}

function renderFramingExperiment(caseData, experiment) {
  const run = experiment.runs[state.runIndex];
  elements.experimentKicker.textContent = "Question-framing intervention";
  elements.experimentTitle.textContent = "How the meaning of “good” changes the inquiry";
  elements.experimentDescription.textContent =
    "The raw question stays fixed. Each run swaps the framing object, which changes the operational question, admissible sources, and shape of the answer.";
  elements.experimentSection.classList.add("framing-experiment");
  elements.runPickerTitle.textContent = "Choose what “good” means";
  elements.runPickerDescription.textContent =
    "Select a framing to rerun the inquiry. The question, admitted sources, exclusions, and resulting assessment update together.";
  elements.coverageDetails.hidden = true;
  elements.framingSidebar.hidden = false;
  elements.assessmentLabel.textContent = "Assessment under this framing";
  elements.supportBalance.hidden = true;
  elements.framingOutput.hidden = false;
  elements.graphFilterField.hidden = true;
  elements.graphTitle.textContent = "Question → framing → source policy → evidence → assessment";
  elements.graphDescription.textContent =
    "This graph shows the dependency introduced before evidence retrieval begins.";
  elements.coverageSummary.textContent = "What this framing admits and excludes";
  elements.graphLegend.replaceChildren(
    el("span", {}, [el("i", { className: "legend-mark question-mark" }), document.createTextNode("Raw question")]),
    el("span", {}, [el("i", { className: "legend-mark framing-mark" }), document.createTextNode("Framing")]),
    el("span", {}, [el("i", { className: "legend-mark policy-mark" }), document.createTextNode("Source policy")]),
    el("span", {}, [el("i", { className: "legend-mark claim-mark" }), document.createTextNode("Evidence")]),
    el("span", {}, [el("i", { className: "legend-mark assessment-mark" }), document.createTextNode("Assessment")]),
  );

  elements.runTitle.textContent = run.label;
  elements.runDescription.textContent = run.operationalized_question;
  elements.runCounts.textContent = `${run.included_evidence_ids.length} evidence record · ${run.included_source_ids.length} cited sources · framing ${run.framing_declared ? "declared" : "implicit"}`;
  elements.assessmentConclusion.textContent = run.assessment_summary;
  elements.answerShape.textContent = run.answer_shape;
  renderFramingGraph(experiment, run, caseData);
  renderFramingCoverage(run);
}

function renderExperiment(caseData) {
  const experiment = currentExperiment();
  elements.experimentSection.hidden = !experiment;
  if (!experiment) return;
  if (state.runIndex >= experiment.runs.length) state.runIndex = 0;
  renderRunTabs(experiment, caseData);
  if (experiment.experiment_type === "fixed_corpus_ablation") {
    renderFixedCorpusExperiment(caseData, experiment);
  } else {
    renderFramingExperiment(caseData, experiment);
  }
}

function filteredEvidence(caseData) {
  const query = state.query.toLowerCase().trim();
  return caseData.evidence.filter((item) => {
    const matchesDirection =
      state.direction === "all" || item.evidence.direction === state.direction;
    const searchable = [
      item.evidence.title,
      item.evidence.claim,
      item.evidence.evidence_type,
      ...item.evidence.citations.map((source) => source.citation),
      JSON.stringify(item.review),
    ]
      .join(" ")
      .toLowerCase();
    return matchesDirection && (!query || searchable.includes(query));
  });
}

function renderEvidenceList(caseData) {
  const items = filteredEvidence(caseData);
  const total = caseData.evidence.length;
  elements.resultCount.textContent =
    items.length === total ? `${total} records` : `${items.length} of ${total} records`;

  if (!items.length) {
    elements.list.replaceChildren(
      el("p", { className: "empty", text: "No records match these filters." }),
    );
    elements.detail.replaceChildren(
      el("p", { className: "empty", text: "Change the search or position filter." }),
    );
    return;
  }

  if (!state.selectedId || !items.some((item) => item.evidence.evidence_id === state.selectedId)) {
    state.selectedId = items[0].evidence.evidence_id;
  }

  elements.list.replaceChildren(
    ...items.map((item) => {
      const evidence = item.evidence;
      const card = el(
        "button",
        {
          className: "evidence-card",
          attrs: {
            type: "button",
            "aria-current": String(evidence.evidence_id === state.selectedId),
          },
        },
        [
          el("div", {
            className: "record-context",
            text: `${label(evidence.direction)} · ${label(evidence.evidence_type)}`,
          }),
          el("h3", { text: evidence.title }),
          el("p", {
            text: `${evidence.citations.length} cited ${evidence.citations.length === 1 ? "source" : "sources"}`,
          }),
        ],
      );
      card.addEventListener("click", () => {
        state.selectedId = evidence.evidence_id;
        renderEvidenceList(caseData);
      });
      return card;
    }),
  );

  renderDetail(
    items.find((item) => item.evidence.evidence_id === state.selectedId),
    caseData,
  );
}

function reviewRow(title, values) {
  if (!values?.length) return null;
  return el("div", { className: "review-row" }, [
    el("dt", { text: title }),
    el("dd", {}, [el("ul", {}, values.map((value) => el("li", { text: value })))]),
  ]);
}

function renderDetail(item, caseData) {
  if (!item) return;
  const evidence = item.evidence;
  const review = item.review;
  const sourceMap = new Map(caseData.sources.map((source) => [source.source_id, source]));

  const sourceNodes = evidence.citations.map((source) => {
    const normalized = sourceMap.get(source.source_id);
    const citation = source.urls[0]
      ? el("a", {
          text: source.citation,
          attrs: { href: source.urls[0], target: "_blank", rel: "noreferrer" },
        })
      : el("span", { text: source.citation });
    return el("li", {}, [
      citation,
      el("p", {
        className: "source-meta",
        text: `${label(source.source_class)} · source text ${label(source.verification_status)}`,
      }),
      normalized?.review?.quality_assessment
        ? el("p", { className: "source-note", text: normalized.review.quality_assessment })
        : null,
      ...(normalized?.review?.independence_notes || []).map((note) =>
        el("p", { className: "source-note warning-text", text: note }),
      ),
    ]);
  });

  const structuralRows = [
    reviewRow("Framing assumption", review.framing_assumptions),
    reviewRow("Policy sensitivity", review.policy_sensitivities),
    reviewRow("Coverage gap", review.coverage_gaps),
    reviewRow("Correlation risk", review.correlation_risks),
    reviewRow("Capability limit", review.capability_limits),
  ].filter(Boolean);

  const uncertainty = review.uncertainty_attribution;
  const uncertaintyRows = [
    reviewRow("Evidence itself", uncertainty.evidential),
    reviewRow("Missing or filtered inputs", uncertainty.ingestion_conditional),
    reviewRow("Analysis capability", uncertainty.capability_conditional),
    reviewRow("Framing choice", uncertainty.framing_conditional),
    reviewRow("Not yet attributed", uncertainty.unattributed),
  ].filter(Boolean);

  const reviewContent = structuralRows.length
    ? [
        el("dl", { className: "review-table" }, structuralRows),
        uncertaintyRows.length
          ? el("p", { className: "subsection-title", text: "Where uncertainty enters" })
          : null,
        uncertaintyRows.length ? el("dl", { className: "review-table" }, uncertaintyRows) : null,
      ]
    : [
        el("p", {
          className: "source-note",
          text: "No structural annotation has been completed for this record.",
        }),
      ];

  const reviewComplete = item.annotation_status === "provisionally_reviewed";
  elements.detail.replaceChildren(
    el("header", { className: "record-header" }, [
      el("div", { className: "detail-meta" }, [
        el("span", { text: label(evidence.direction) }),
        el("span", { text: label(evidence.evidence_type) }),
        el("span", {
          text: `${evidence.citations.length} ${evidence.citations.length === 1 ? "source" : "sources"}`,
        }),
      ]),
      el("h2", { text: evidence.title }),
    ]),
    el("section", { className: "claim-section" }, [
      el("h3", { text: "Claim in the supplied baseline" }),
      el("p", { className: "claim-text", text: evidence.claim }),
    ]),
    el("section", { className: "review-section" }, [
      el("h3", { text: "Structural annotation" }),
      el("div", { className: "review-status" }, [
        el("strong", {
          text: reviewComplete ? "Evidence note reviewed" : "Structural review pending",
        }),
        el("span", { text: "Source-text verification not performed" }),
      ]),
      ...reviewContent,
    ]),
    el("section", { className: "baseline-section" }, [
      el("h3", { text: "Assessment supplied with the baseline" }),
      el("div", { className: "baseline-grid" }, [
        el("div", {}, [
          el("h4", { text: "Evidence quality" }),
          el("p", { text: evidence.evidence_quality || "Not supplied." }),
        ]),
        el("div", {}, [
          el("h4", { text: "Strongest counterargument" }),
          el("p", { text: evidence.strongest_counterargument || "Not supplied." }),
        ]),
      ]),
    ]),
    el("section", { className: "sources-section" }, [
      el("h3", { text: `Cited sources (${evidence.citations.length})` }),
      el("ul", { className: "source-list" }, sourceNodes),
    ]),
  );
}

function renderPolicies(caseData) {
  if (currentExperiment()) {
    elements.policySection.hidden = true;
    elements.policies.replaceChildren();
    return;
  }
  const policies = state.catalog.policies.filter(
    (policy) => policy.case_id === caseData.manifest.case_id,
  );
  elements.policySection.hidden = policies.length === 0;
  if (!policies.length) {
    elements.policies.replaceChildren();
    return;
  }

  elements.policyDescription.textContent =
    "Each definition fixes a different meaning of the question before evidence is selected.";
  elements.policies.replaceChildren(
    ...policies.map((policy) =>
      el("article", { className: "policy-card" }, [
        el("div", {
          className: "record-context",
          text: label(policy.framing.framing_id),
        }),
        el("h3", { text: policy.framing.operationalized_question }),
        el("p", { text: `Version ${policy.version} · ${policy.policy_id}` }),
        el("ul", {}, [
          ...policy.source_scope.inclusion_rules.map((rule) =>
            el("li", { text: `Includes: ${rule}` }),
          ),
          ...policy.source_scope.exclusion_rules.map((rule) =>
            el("li", { text: `Excludes: ${rule}` }),
          ),
        ]),
      ]),
    ),
  );
}

function render() {
  const caseData = currentCase();
  renderTabs();
  renderCaseHeader(caseData);
  renderExperiment(caseData);
  renderEvidenceList(caseData);
  renderPolicies(caseData);
}

elements.search.addEventListener("input", (event) => {
  state.query = event.target.value;
  renderEvidenceList(currentCase());
});

elements.direction.addEventListener("change", (event) => {
  state.direction = event.target.value;
  renderEvidenceList(currentCase());
});

elements.clusterFilter.addEventListener("change", (event) => {
  state.clusterId = event.target.value;
  const experiment = currentExperiment();
  if (experiment?.experiment_type === "fixed_corpus_ablation") {
    renderClaimGraph(experiment, experiment.runs[state.runIndex], currentCase());
  }
});

try {
  const response = await fetch("./data/catalog.json");
  if (!response.ok) throw new Error(`Data request failed: ${response.status}`);
  state.catalog = await response.json();
  render();
} catch (error) {
  console.error(error);
  elements.list.replaceChildren(
    el("p", {
      className: "empty",
      text: "The generated catalog is missing. Run the Python build step first.",
    }),
  );
}
