const courseLinks = {
  instructorRepo: "https://github.com/skgallagher/stat-methods-ai-instructor",
  publicRepo: "https://github.com/skgallagher/stat-methods-ai-public",
  publicBlob: "https://github.com/skgallagher/stat-methods-ai-public/blob/main",
  publicRaw: "https://raw.githubusercontent.com/skgallagher/stat-methods-ai-public/main",
  colabBase: "https://colab.research.google.com/github/skgallagher/stat-methods-ai-public/blob/main",
  projectDataBox: "https://cmu.box.com/s/9jzjm8u9wc9kmkmewsoi9ciekbkf5c2k"
};

const siteSettings = {
  // Use "scheduled" when the course is live. Preview shows one chosen week.
  moduleReleaseMode: "preview",
  previewWeek: 2
};

const weeklyMaterials = [
  {
    week: 1,
    label: "Week 1",
    publishDate: "2027-01-17",
    title: "Logistic Regression to Neural Networks",
    description: "Build a one-hidden-layer network from familiar statistical pieces, then compare a baseline and a vision system on genuinely new cameras.",
    links: [
      { label: "Lecture A", href: `${courseLinks.publicBlob}/weeks/week01/lecture_a.html` },
      { label: "Lecture B", href: `${courseLinks.publicBlob}/weeks/week01/lecture_b.html` },
      { label: "Data release", href: `${courseLinks.publicBlob}/data/course/camera_traps/README.md` },
      {
        label: "Lab notebook",
        href: `${courseLinks.publicBlob}/weeks/week01/lab_starter.ipynb`,
        openDate: "2027-01-21"
      },
      {
        label: "Open lab in Colab",
        href: `${courseLinks.colabBase}/weeks/week01/lab_starter.ipynb`,
        openDate: "2027-01-21"
      },
      {
        label: "HW1 PDF",
        href: `${courseLinks.publicBlob}/weeks/week01/hw01.pdf`,
        openDate: "2027-01-21"
      },
      {
        label: "HW1 notebook",
        href: `${courseLinks.publicBlob}/weeks/week01/hw01_starter.ipynb`,
        openDate: "2027-01-21"
      },
      {
        label: "Open HW1 in Colab",
        href: `${courseLinks.colabBase}/weeks/week01/hw01_starter.ipynb`,
        openDate: "2027-01-21"
      }
    ]
  },
  {
    week: 2,
    label: "Week 2",
    publishDate: "2027-01-24",
    title: "Data as Measurement: Labels and Disagreement",
    description: "Use repeated DynaSent judgments to study label distributions, conditional and marginal dependence, hard and soft targets, and Brier score.",
    links: [
      { label: "Lecture A", href: `${courseLinks.publicBlob}/weeks/week02/lecture_a.html` },
      { label: "Lecture B", href: `${courseLinks.publicBlob}/weeks/week02/lecture_b.html` },
      { label: "Data release", href: `${courseLinks.publicBlob}/data/course/dynasent/README.md` },
      {
        label: "Lab notebook",
        href: `${courseLinks.publicBlob}/weeks/week02/lab.ipynb`,
        openDate: "2027-01-28"
      },
      {
        label: "Open lab in Colab",
        href: `${courseLinks.colabBase}/weeks/week02/lab.ipynb`,
        openDate: "2027-01-28"
      },
      {
        label: "HW2 PDF",
        href: `${courseLinks.publicBlob}/weeks/week02/hw02.pdf`,
        openDate: "2027-01-28"
      },
      {
        label: "HW2 notebook",
        href: `${courseLinks.publicBlob}/weeks/week02/hw02_starter.ipynb`,
        openDate: "2027-01-28"
      },
      {
        label: "Open HW2 in Colab",
        href: `${courseLinks.colabBase}/weeks/week02/hw02_starter.ipynb`,
        openDate: "2027-01-28"
      }
    ]
  },
  {
    week: 3,
    label: "Week 3",
    publishDate: "2027-01-31",
    title: "Using AI in a Statistical Workflow",
    description: "Prompting, verification, reproducibility, and meta-evaluating AI tools used in analysis.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week03/` }
    ]
  },
  {
    week: 4,
    label: "Week 4",
    publishDate: "2027-02-07",
    title: "Benchmarks Are Sampling Designs",
    description: "Benchmark design, leakage, label quality, target populations, and what test sets can support.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week04/` }
    ]
  },
  {
    week: 5,
    label: "Week 5",
    publishDate: "2027-02-14",
    title: "Accuracy Is an Estimate",
    description: "Performance metrics, confidence intervals, baseline comparisons, and decision costs.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week05/` }
    ]
  },
  {
    week: 6,
    label: "Week 6",
    publishDate: "2027-02-21",
    title: "Calibration and Confidence",
    description: "Reliability diagrams, confidence scores, calibration checks, and midterm review. No homework this week.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week06/` }
    ]
  },
  {
    week: 7,
    label: "Week 7",
    publishDate: "2027-02-28",
    title: "Midterm and Synthesis",
    description: "Synthesis of representation, benchmarks, estimation, and calibration. Closed-book, no-AI midterm.",
    links: [
      { label: "Review Materials", href: `${courseLinks.publicBlob}/weeks/week07/` }
    ]
  },
  {
    week: 8,
    label: "Week 8",
    publishDate: "2027-03-14",
    title: "Distribution Shift",
    description: "Representativeness, shifted populations, project launch, and first evaluation questions.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week08/` }
    ]
  },
  {
    week: 9,
    label: "Week 9",
    publishDate: "2027-03-21",
    title: "Robustness and Ablation",
    description: "Sensitivity analysis, perturbations, ablations, and Project Checkpoint 1.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week09/` },
      { label: "Checkpoint 1", href: `${courseLinks.publicBlob}/projects/checkpoints/checkpoint01.md` }
    ]
  },
  {
    week: 10,
    label: "Week 10",
    publishDate: "2027-03-28",
    title: "Model Comparison Under Realistic Decision Costs",
    description: "Class-specific errors, asymmetric loss, human review thresholds, and client-facing interpretation.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week10/` }
    ]
  },
  {
    week: 11,
    label: "Week 11",
    publishDate: "2027-04-04",
    title: "Calibration in the Wild",
    description: "Stratified calibration, high-confidence errors, judge agreement, and Project Checkpoint 2.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week11/` },
      { label: "Checkpoint 2", href: `${courseLinks.publicBlob}/projects/checkpoints/checkpoint02.md` }
    ]
  },
  {
    week: 12,
    label: "Week 12",
    publishDate: "2027-04-11",
    title: "Human Evaluation as Experimental Design",
    description: "Human feedback as data, rubrics, rater agreement, measurement bias, and labeling protocols.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week12/` }
    ]
  },
  {
    week: 13,
    label: "Week 13",
    publishDate: "2027-04-18",
    title: "Statistical Argument and Client Recommendation",
    description: "Final claims, limitations, robustness, ending artifact, and video planning.",
    links: [
      { label: "Materials", href: `${courseLinks.publicBlob}/weeks/week13/` },
      { label: "Ending Artifact", href: `${courseLinks.publicBlob}/projects/checkpoints/ending_artifact.md` }
    ]
  },
  {
    week: 14,
    label: "Week 14",
    publishDate: "2027-04-25",
    title: "Project Presentations and Course Synthesis",
    description: "Recorded videos, oral discussions, final reports, and course synthesis.",
    links: [
      { label: "Final Project", href: `${courseLinks.publicBlob}/projects/final_project.md` }
    ]
  }
];

const projectDocs = [
  {
    label: "Project data downloads",
    href: courseLinks.projectDataBox,
    actionLabel: "Open Box folder",
    openDate: "2027-03-14",
    status: "Four frozen course bundles with starter notebooks, cached AI outputs, provenance, and sealed holdouts · opens with the Week 8 project launch"
  },
  {
    label: "Project statement",
    href: null,
    status: "Student-facing overview and deliverables · coming later"
  },
  {
    label: "Project rubric",
    href: null,
    status: "Weights and evaluation criteria · coming later"
  },
  {
    label: "Datasets and baselines",
    href: null,
    status: "Supported choices and baseline cookbook · coming later"
  }
];
