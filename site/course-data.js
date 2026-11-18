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
  // The Box folder "Stat-AI Spring 2027 project data" (CMU sign-in). The starters download
  // its zips through their own open links, listed in the starters and in box_downloads.json.
  projectDataBox: "https://cmu.box.com/s/mvwydnvoc3ymlq3jusan0p9kkbank1s7"
};

const siteSettings = {
  // "scheduled": a week appears after its Sunday publishDate (use when the course is live).
  // "preview": show only previewWeek, with lab and homework links locked until their openDate.
  // "beta": show Weeks 1 through betaThroughWeek with every link open, for testers.
  moduleReleaseMode: "beta",
  previewWeek: 2,
  betaThroughWeek: 15
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
    homework: { label: "HW1", due: "Jan 26", pdf: `${courseLinks.publicBlob}/weeks/week01/hw01.pdf`, links: notebook("weeks/week01/hw01_starter.ipynb", "2027-01-17T13:00"), openDate: "2027-01-17T13:00" },
    data: [dataRelease("Camera Traps data", "camera_traps")]
  },
  {
    week: 2, dates: "Jan 26 / 28", publishDate: "2027-01-24",
    topic: "Data as measurement: labels and repeated judgments",
    slides: slides("week02"),
    lab: notebook("weeks/week02/lab.ipynb", "2027-01-28"),
    homework: { label: "HW2", due: "Feb 2", pdf: `${courseLinks.publicBlob}/weeks/week02/hw02.pdf`, links: notebook("weeks/week02/hw02_starter.ipynb", "2027-01-24T13:00"), openDate: "2027-01-24T13:00" },
    data: [dataRelease("DynaSent data", "dynasent")]
  },
  {
    week: 3, dates: "Feb 2 / 4", publishDate: "2027-01-31",
    topic: "Evaluation design: estimands, splits, and AI-assisted workflow",
    slides: slides("week03"),
    lab: notebook("weeks/week03/lab_starter.ipynb", "2027-02-04"),
    homework: { label: "HW3", due: "Feb 9", pdf: `${courseLinks.publicBlob}/weeks/week03/hw03.pdf`, links: notebook("weeks/week03/hw03_starter.ipynb", "2027-01-31T13:00"), openDate: "2027-01-31T13:00" },
    data: [dataRelease("CFPB data", "cfpb"), dataRelease("GitHub issues data", "github_issues")]
  },
  {
    week: 4, dates: "Feb 9 / 11", publishDate: "2027-02-07",
    topic: "Benchmark performance as estimation",
    slides: slides("week04"),
    lab: notebook("weeks/week04/lab_starter.ipynb", "2027-02-11"),
    homework: { label: "HW4", due: "Feb 16", pdf: `${courseLinks.publicBlob}/weeks/week04/hw04.pdf`, links: notebook("weeks/week04/hw04_starter.ipynb", "2027-02-07T13:00"), openDate: "2027-02-07T13:00" },
    data: [dataRelease("Camera Traps data", "camera_traps")]
  },
  {
    week: 5, dates: "Feb 16 / 18", publishDate: "2027-02-14",
    topic: "Paired system comparison",
    slides: slides("week05"),
    lab: notebook("weeks/week05/lab_starter.ipynb", "2027-02-18"),
    homework: { label: "HW5", due: "Feb 23", pdf: `${courseLinks.publicBlob}/weeks/week05/hw05.pdf`, links: notebook("weeks/week05/hw05_starter.ipynb", "2027-02-14T13:00"), openDate: "2027-02-14T13:00" },
    data: [dataRelease("BIG-Bench Hard data", "llm_bbh")]
  },
  {
    week: 6, dates: "Feb 23 / 25", publishDate: "2027-02-21",
    topic: "Calibration and decision-rule sensitivity",
    note: "No homework; midterm practice on Canvas",
    slides: slides("week06"),
    lab: notebook("weeks/week06/lab_starter.ipynb", "2027-02-25"),
    data: [dataRelease("BIG-Bench Hard data", "llm_bbh")]
  },
  {
    week: 7, dates: "Mar 2 / 4", publishDate: "2027-02-28",
    topic: "First-half synthesis",
    note: "In-class midterm Thu Mar 4",
    slides: [{ label: "Tue", href: `${courseLinks.pagesBase}/weeks/week07/lecture_a.html` }]
  },
  { week: 8, dates: "Mar 9 / 11", publishDate: null, topic: "Spring break", isBreak: true },
  {
    week: 9, dates: "Mar 16 / 18", publishDate: "2027-03-14",
    topic: "Distribution shift and project launch",
    note: "No homework; project launch Thu Mar 18",
    slides: slides("week09"),
    lab: notebook("weeks/week09/lab_starter.ipynb", "2027-03-18"),
    data: [dataRelease("Camelyon17 data", "camelyon17")]
  },
  {
    week: 10, dates: "Mar 23 / 25", publishDate: "2027-03-21",
    topic: "Sensitivity analysis",
    note: "Project Milestone 1 due Mar 23",
    slides: slides("week10"),
    lab: notebook("weeks/week10/lab_starter.ipynb", "2027-03-25"),
    homework: { label: "HW6", due: "Mar 30", pdf: `${courseLinks.publicBlob}/weeks/week10/hw06.pdf`, links: notebook("weeks/week10/hw06_starter.ipynb", "2027-03-21T13:00"), openDate: "2027-03-21T13:00" },
    data: [dataRelease("Camelyon17 data", "camelyon17")]
  },
  {
    week: 11, dates: "Mar 30 / Apr 1", publishDate: "2027-03-28",
    topic: "Designed AI evaluations",
    note: "No homework; project work session Thu Apr 1",
    slides: slides("week11"),
    lab: notebook("weeks/week11/lab_starter.ipynb", "2027-04-01"),
    data: [dataRelease("GSM8K answers data", "llm_gsm8k")]
  },
  {
    week: 12, dates: "Apr 6 / 8", publishDate: "2027-04-04",
    topic: "LLM judges as measurement instruments",
    note: "Project Milestone 2 due Sun Apr 11",
    slides: slides("week12"),
    lab: notebook("weeks/week12/lab_starter.ipynb", "2027-04-08"),
    homework: { label: "HW7", due: "Apr 13", pdf: `${courseLinks.publicBlob}/weeks/week12/hw07.pdf`, links: notebook("weeks/week12/hw07_starter.ipynb", "2027-04-04T13:00"), openDate: "2027-04-04T13:00" },
    data: [dataRelease("MT-Bench judgments data", "llm_judges")]
  },
  {
    week: 13, dates: "Apr 13", publishDate: "2027-04-11",
    topic: "Human-centered and responsible AI",
    note: "Guest lecture by Carol J. Smith Tue · no class Thu (Spring Carnival)",
    slides: [{ label: "Guest lecture and readings", href: `${courseLinks.publicBlob}/weeks/week13/guest_lecture.md` }]
  },
  {
    week: 14, dates: "Apr 20 / 22", publishDate: "2027-04-18",
    topic: "Writing in your own voice",
    note: "Project Milestone 3 due Apr 20 · storyboard feedback and team meetings Thu",
    slides: slides("week14"),
    lab: [{ label: "Work session guide", href: `${courseLinks.publicBlob}/weeks/week14/studio.md` }]
  },
  {
    week: 15, dates: "Apr 27 / 29", publishDate: "2027-04-25",
    topic: "Oral presentations",
    note: "Slides and video due Sun Apr 25",
    slides: [{ label: "Tue / Thu", href: `${courseLinks.pagesBase}/weeks/week15/lecture_a.html` }]
  }
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
    status: "Data and cached AI outputs for all four tracks, one zip per track. Opens at the end of spring break, when teams and tracks are posted."
  },
  {
    label: "Starter notebooks",
    status: "One Colab notebook per track; its first cell downloads that track's data. Opens at the end of spring break, with the data.",
    links: [
      { label: "Food tagging", href: `${courseLinks.colabBase}/project/tracks/track_1_food/starter.ipynb`, openDate: "2027-03-14" },
      { label: "Pet tagging", href: `${courseLinks.colabBase}/project/tracks/track_2_pets/starter.ipynb`, openDate: "2027-03-14" },
      { label: "Human preferences", href: `${courseLinks.colabBase}/project/tracks/track_3_preferences/starter.ipynb`, openDate: "2027-03-14" },
      { label: "Instruction following", href: `${courseLinks.colabBase}/project/tracks/track_4_instructions/starter.ipynb`, openDate: "2027-03-14" }
    ]
  }
];
