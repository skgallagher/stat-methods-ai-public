# Statistical Methods for AI — Instructor Repo (Private)

This repo mirrors the structure of your existing course repo.

## What lives where
- **Student-facing** materials live in the top-level folders (e.g., `weeks/`, `labs/`, `lecture_drafts/`, `homeworks/`, etc.).
- **Instructor-only** materials live in `instructor_only/` (solutions, rubrics, grading notes).

## Publishing to the public repo
A GitHub Action publishes this repo to the public repo by syncing **everything** except excluded folders:
- `instructor_only/`
- `grades/`
- (optionally) `exam/` (if you keep exams private)

Workflow: `.github/workflows/publish_public.yml`

## Official runtime
- Google Colab (Chrome recommended)
- Optional local: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
