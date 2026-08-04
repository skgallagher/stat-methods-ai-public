# Course Website

This is a static, no-build course website.

The site is intentionally linked to the GitHub repos rather than duplicating course materials. Weekly slides, labs, homework, and project handouts should live in the public repo after the instructor repo publishes. The website points to those canonical files.

The information architecture is deliberately small. The persistent navigation
has five choices: Home, Weekly materials, Final project, Syllabus, and GitHub.
The homepage contains the current release and essential course information; the
complete calendar lives with weekly materials; detailed project information
lives on the project page; and policies live in the syllabus.

## Files

- `index.html` — course landing page, current release, five-step workflow, and course essentials
- `modules.html` — released materials and complete course calendar
- `project.html` — final project overview
- `syllabus.html` — course overview, grading, policies, and student support
- `styles.css` — site styling
- `course-data.js` — central repo URLs and material links
- `site.js` — small renderer for repo/material links

## Update Pattern

When adding a new week, update `weeklyMaterials` in `course-data.js`.

When adding canonical project files, update `projectDocs` in `course-data.js`.
Until a file is actually public, give it a null `href`; the site will render a
non-clickable “Coming soon” state rather than a broken link.

## Weekly Sunday Release

Each module in `course-data.js` has a `publishDate` field. The modules page sorts released weeks newest first.

During development, show one selected week while still honoring lab and homework
opening dates:

```js
moduleReleaseMode: "preview",
previewWeek: 1
```

When the course is live:

```js
moduleReleaseMode: "scheduled"
```

In scheduled mode, a module appears only after its Sunday `publishDate`. This lets the site update weekly without editing the HTML.

Individual links may also declare an `openDate`. Before that date, the site
renders a clearly labeled, non-clickable lock instead of an anchor. Week 1 uses
this for the lab and homework while leaving the lectures and data release
available. This is a navigation gate only: files already committed to the
public GitHub repository remain discoverable there.

The website can be copied to a CMU Statistics web directory as static files. It will still link to the latest materials in the public GitHub repo.
