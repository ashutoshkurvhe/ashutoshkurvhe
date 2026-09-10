# Validation — Obsidian profile 27

Checked locally on 2026-09-09.

- 10 focused unit tests pass: unfinished current day, year boundary, inactive day, missing-day gap, singular/plural and comma-formatted counts, legacy count attributes, malformed/error pages, duplicate calendar cells, and valid SVG output from the real snapshot.
- 39 local SVG assets parse and render successfully. Desktop/mobile banner, project artwork, overview, streak, language chart and contribution calendar are included.
- All 40 local image references in README resolve. Every image has descriptive alternative text. No inline CSS, scripts, SVG markup or iframe is embedded directly into README HTML.
- Every one of the supplied README's 20 technology entries is retained.
- Public GitHub REST calls succeeded for the account, its 16 public repositories, their language data, and public authored issue/PR counts.
- The featured Personal-Productivity-OS repository and five additional public project links appear in the fetched repository inventory. RouteWise is deliberately not linked as a public repository.
- 617 daily contribution records were parsed and validated without missing dates, covering 2025-01-01 through 2026-09-09. The latest 365-day window is 2025-09-10 through 2026-09-09 and sums to 1,424. The observed history total is 1,666; current streak 3 days; longest 20 days.
- The public counter endpoint returned SVG during creation. It is the only external image service in the README and is not guaranteed to remain available.
- Workflow YAML parses; the checkout action's pinned SHA was resolved from the official actions/checkout v4 tag. The scheduled task only stages metric assets and the public data snapshot, using the GitHub Actions bot identity.
- The included PNG previews were composed from rendered local SVG assets and representative Markdown text layout. They are **not screenshots of a deployed GitHub profile**. GitHub's exact HTML rendering, surrounding UI and image caching remain platform-controlled.

The profile repository was not modified. The workflow has not been executed on GitHub because this task creates a downloadable package. Run it once after uploading, as described in SETUP.md. Public-calendar HTML is an unversioned source; future changes may require a parser update. Fetch or parse failures stop before old cards are replaced.
