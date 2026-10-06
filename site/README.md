# Course Website

A static, no-build site. It links to the canonical files in the public repo rather than copying them. Slides open through GitHub Pages (`https://skgallagher.github.io/stat-methods-ai-public/`), and notebooks open in Colab.

## Files

- `index.html`: home page with this week's materials, a short course description, and key facts
- `modules.html`: the schedule table for all 15 weeks, with slides, labs, and homework for released weeks
- `project.html`: final project overview, tracks, and deliverables
- `syllabus.html`: built from `syllabus.md` by `stat-ai-gpt/scripts/build_site_syllabus.py`; `syllabus.pdf` is the printable copy
- `course-data.js`: links, release settings, and one entry per week
- `site.js`: renders the schedule, this week's box, and project resources
- `styles.css`: site styling

## Adding a week

Add `slides`, `lab`, `homework`, and `data` to that week's entry in `course-data.js`. Weeks without `slides` show their topic only.

## Release modes

Set `siteSettings.moduleReleaseMode` in `course-data.js`:

- `"beta"`: Weeks 1 through `betaThroughWeek` are shown with every link open (for testers).
- `"preview"`: only `previewWeek` is shown, with lab and homework links locked until their `openDate`.
- `"scheduled"`: a week appears after its Sunday `publishDate`, and lab and homework links open on their `openDate` (use when the course is live).

The lock is navigation only. Files committed to the public repo remain reachable there.

## After editing

Bump the `?v=` number on the CSS and JS links in each page (and in `build_site_syllabus.py`) so browsers do not keep an old copy.
