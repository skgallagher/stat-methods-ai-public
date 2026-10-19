const courseLinks = {
  instructorRepo: "https://github.com/skgallagher/stat-methods-ai-instructor",
  publicRepo: "https://github.com/skgallagher/stat-methods-ai-public",
  publicBlob: "https://github.com/skgallagher/stat-methods-ai-public/blob/main",
  publicRaw: "https://raw.githubusercontent.com/skgallagher/stat-methods-ai-public/main",
  colabBase: "https://colab.research.google.com/github/skgallagher/stat-methods-ai-public/blob/main",
  // The course website lives here. Copies opened on GitHub Pages forward to it.
  siteHome: "https://www.stat.cmu.edu/~sgallagh/courses/stat-ai-spring-2027/",
  // GitHub Pages serves the public repo, so HTML slides render in the browser.
  pagesBase: "https://skgallagher.github.io/stat-methods-ai-public",
  projectDataBox: "https://cmu.box.com/s/9jzjm8u9wc9kmkmewsoi9ciekbkf5c2k"
};

const siteSettings = {
  // "scheduled": a week appears after its Sunday publishDate (use when the course is live).
  // "preview": show only previewWeek, with lab and homework links locked until their openDate.
  // "beta": show Weeks 1 through betaThroughWeek with every link open, for testers.
  moduleReleaseMode: "beta",
  previewWeek: 2,
  betaThroughWeek: 6
};

// Helpers so each week below stays short.
const slides = (week) => [
  { label: "Tue", href: `${courseLinks.pagesBase}/weeks/${week}/lecture_a.html` },
  { label: "Thu", href: `${courseLinks.pagesBase}/weeks/${week}/lecture_b.html` }
];
const notebook = (path, openDate) => [
  { label: "Colab", href: `${courseLinks.colabBase}/${path}`, openDate },
  { label: "notebook", href: `${courseLinks.publicBlob}/${path}`, openDate }
];
const dataRelease = (label, folder) => ({ label, href: `${courseLinks.publicBlob}/data/course/${folder}/README.md` });

// One entry per week. Topics and dates follow the syllabus calendar.
const weeklyMaterials = [
  {
    week: 1, dates: "Jan 19 / 21", publishDate: "2027-01-17",
    topic: "From regression to neural networks",
    slides: slides("week01"),
    lab: notebook("weeks/week01/lab_starter.ipynb", "2027-01-21"),
    homework: { label: "HW1", due: "Jan 26", pdf: `${courseLinks.publicBlob}/weeks/week01/hw01.pdf`, links: notebook("weeks/week01/hw01_starter.ipynb", "2027-01-21"), openDate: "2027-01-21" },
    data: [dataRelease("Camera Traps data", "camera_traps")]
  },
  {
    week: 2, dates: "Jan 26 / 28", publishDate: "2027-01-24",
    topic: "Data as measurement: labels and repeated judgments",
    slides: slides("week02"),
    lab: notebook("weeks/week02/lab.ipynb", "2027-01-28"),
    homework: { label: "HW2", due: "Feb 2", pdf: `${courseLinks.publicBlob}/weeks/week02/hw02.pdf`, links: notebook("weeks/week02/hw02_starter.ipynb", "2027-01-28"), openDate: "2027-01-28" },
    data: [dataRelease("DynaSent data", "dynasent")]
  },
  {
    week: 3, dates: "Feb 2 / 4", publishDate: "2027-01-31",
    topic: "Evaluation design: estimands, splits, and AI-assisted workflow",
    slides: slides("week03"),
    lab: notebook("weeks/week03/lab_starter.ipynb", "2027-02-04"),
    homework: { label: "HW3", due: "Feb 9", pdf: `${courseLinks.publicBlob}/weeks/week03/hw03.pdf`, links: notebook("weeks/week03/hw03_starter.ipynb", "2027-02-04"), openDate: "2027-02-04" },
    data: [dataRelease("CFPB data", "cfpb"), dataRelease("GitHub issues data", "github_issues")]
  },
  {
    week: 4, dates: "Feb 9 / 11", publishDate: "2027-02-07",
    topic: "Benchmark performance as estimation",
    slides: slides("week04"),
    lab: notebook("weeks/week04/lab_starter.ipynb", "2027-02-11"),
    homework: { label: "HW4", due: "Feb 16", pdf: `${courseLinks.publicBlob}/weeks/week04/hw04.pdf`, links: notebook("weeks/week04/hw04_starter.ipynb", "2027-02-11"), openDate: "2027-02-11" },
    data: [dataRelease("Camera Traps data", "camera_traps")]
  },
  {
    week: 5, dates: "Feb 16 / 18", publishDate: "2027-02-14",
    topic: "Paired system comparison",
    slides: slides("week05"),
    lab: notebook("weeks/week05/lab_starter.ipynb", "2027-02-18"),
    homework: { label: "HW5", due: "Feb 23", pdf: `${courseLinks.publicBlob}/weeks/week05/hw05.pdf`, links: notebook("weeks/week05/hw05_starter.ipynb", "2027-02-18"), openDate: "2027-02-18" },
    data: [dataRelease("BIG-Bench Hard data", "llm_bbh")]
  },
  {
    week: 6, dates: "Feb 23 / 25", publishDate: "2027-02-21",
    topic: "Calibration and decision-rule sensitivity",
    note: "No homework; midterm practice instead",
    slides: slides("week06"),
    lab: notebook("weeks/week06/lab_starter.ipynb", "2027-02-25"),
    homework: { label: "Midterm practice", due: "Mar 2 for feedback", pdf: `${courseLinks.publicBlob}/weeks/week06/midterm_review.pdf`, links: [{ label: "exam-format practice", href: `${courseLinks.publicBlob}/weeks/week06/midterm_theory_practice.pdf`, openDate: "2027-02-23" }], openDate: "2027-02-23" },
    data: [dataRelease("BIG-Bench Hard data", "llm_bbh")]
  },
  { week: 7, dates: "Mar 2 / 4", publishDate: "2027-02-28", topic: "First-half synthesis", note: "In-class midterm Thu Mar 4" },
  { week: 8, dates: "Mar 9 / 11", publishDate: null, topic: "Spring break", isBreak: true },
  { week: 9, dates: "Mar 16 / 18", publishDate: "2027-03-14", topic: "Distribution shift and project launch" },
  { week: 10, dates: "Mar 23 / 25", publishDate: "2027-03-21", topic: "Sensitivity analysis", note: "Project Milestone 1 due Mar 23" },
  { week: 11, dates: "Mar 30 / Apr 1", publishDate: "2027-03-28", topic: "Designed AI evaluations" },
  { week: 12, dates: "Apr 6 / 8", publishDate: "2027-04-04", topic: "LLM judges as measurement instruments", note: "Project Milestone 2 due Apr 6" },
  { week: 13, dates: "Apr 13", publishDate: "2027-04-11", topic: "Human-centered and responsible AI", note: "Guest lecture Tue · no class Thu (Spring Carnival)" },
  { week: 14, dates: "Apr 20 / 22", publishDate: "2027-04-18", topic: "Statistical argument and recommendation", note: "Project Milestone 3 due Apr 20" },
  { week: 15, dates: "Apr 27 / 29", publishDate: "2027-04-25", topic: "Oral defenses and course synthesis", note: "Slides and video due Sun Apr 25" }
];

const projectDocs = [
  {
    label: "Project Description",
    href: "project_description.pdf",
    actionLabel: "PDF",
    status: "The client, the four tracks, how to tell the study as one story, and what each deliverable contains, with dates."
  },
  {
    label: "Project Rubric",
    href: "project_rubric.pdf",
    actionLabel: "PDF",
    status: "How every deliverable is graded, in points."
  },
  {
    label: "Project data",
    href: courseLinks.projectDataBox,
    actionLabel: "Box folder",
    openDate: "2027-03-14",
    status: "Data, cached AI outputs, and starter notebooks for all four tracks. Opens with the project launch in Week 9."
  }
];
