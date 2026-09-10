# Obsidian — design 27

This package is the working README adaptation of the selected charcoal/lime concept for **Ashutosh Kurvhe / ashutoshkurvhe**. It includes the real README, editable SVG assets, a real-data snapshot, and a daily GitHub Actions refresh.

## Sabse pehle: sirf README paste mat karna

`README.md` ke saath `assets/` folder bhi upload karna zaroori hai. Images isi folder se load hoti hain. Automatic statistics refresh ke liye `.github/`, `scripts/`, `tests/` aur `data/` bhi include karo. ZIP ko extract karo; ZIP file ko repository mein upload nahi karna hai.

The contents go in the root of your existing public **ashutoshkurvhe/ashutoshkurvhe** repository, on its default branch. Do not put them inside an extra `obsidian-profile` subfolder. Keep unrelated existing repository files.

## Fast setup on GitHub

1. Download and extract `Obsidian-Profile-27.zip`.
2. Open [your profile repository](https://github.com/ashutoshkurvhe/ashutoshkurvhe). Keep a backup of the old README if desired.
3. Replace the root `README.md` and upload the package folders to the same repository root. The workflow must be at `.github/workflows/refresh-profile.yml`, including the leading dot in `.github`.
4. Commit to your default branch. No personal access token or external hosting is required.
5. Open **Actions → Refresh Obsidian profile → Run workflow**. Select the default branch. The workflow may also start automatically when the README/scripts/workflow are committed.
6. Wait for a successful run, then reopen your profile. Confirm the date on the overview card. The included snapshot is already usable before the first run.

The workflow is scheduled for **02:17 UTC / 07:47 IST daily**. GitHub scheduled jobs can be delayed. Schedules run from the default branch and may be disabled after prolonged repository inactivity. These are GitHub scheduling rules, not a promise of an exact execution time. You can run the workflow manually at any time.

## If you use a local clone / PowerShell

Copy the extracted files into your existing profile repository checkout, then run:

```powershell
# Run inside your existing ashutoshkurvhe profile repository.
git status
git add README.md assets scripts tests data .github/workflows/refresh-profile.yml SETUP.md .gitignore
git diff --cached --stat
git commit -m "Redesign profile with Obsidian theme"
git push
```

Review the staged files before committing. These commands do not choose a different branch or change your remote. If your branch is protected, use your normal pull-request process. The scheduled bot also needs an allowed path to commit refreshed assets; it does not bypass branch rules.

## What changed

| Existing element | Obsidian implementation |
|---|---|
| Name / introduction | Responsive charcoal/lime SVG banner; updated full-stack introduction |
| About me | MERN/TypeScript work, current projects, JavaScript DSA and system-design practice |
| LinkedIn and email | Existing destinations preserved; consistent local badges |
| All 20 technology entries | Local badges grouped into Languages, Frontend, Backend & database, Developer tools |
| GitHub statistics | Locally stored overview SVG with real public metrics |
| Contribution streak | Locally calculated current/longest streak, with explicit time scope |
| Top languages | Source-byte composition of eligible public repositories |
| Contribution calendar | Additional charcoal/lime calendar inside the README |
| Pinned project content | Two featured projects plus five existing public repository links in a collapsible section |
| Visitor counter | A small Komarev counter replaces the old visitcount endpoint |

No technology from the supplied README was removed. There are no invented skill ratings, rankings, work results or achievements. RouteWise is described as in development with a private repository; it is not given a public link. Personal Productivity OS links to the public repository verified during creation.

The visitor counter is a third-party service and is optional. Its count is not imported from the old provider, is not a unique-person count, and may be affected by image requests/caching. Remove the final counter paragraph from README if you prefer no external badge dependency. All other visual assets and statistics are repository-hosted.

## What a README cannot change

A profile README **cannot recolor GitHub's native avatar/sidebar, achievements, pinned-repository cards, contribution heatmap, activity radar, contribution timeline, navigation or footer**. It also cannot force visitors to use dark mode. GitHub strips inline styles and scripts from rendered Markdown.

The themed contribution calendar in this package is an additional README card. It does not replace or recolor the native calendar below your pinned repositories. Text links rendered by GitHub use the viewer's GitHub theme. Most prominent links use matching image badges; secondary links inside collapsed details remain normal GitHub links.

For your own viewing preference, GitHub **Settings → Appearance → Dark default** is the closest match. Other visitors retain their own settings. The artwork remains intentionally dark on either theme. You may reorder pins and edit the sidebar bio manually; a suitable short bio is:

> Full Stack Developer | React, Node.js & TypeScript | Building useful web applications

## How the numbers work

- **Overview:** public repositories, stars on owned non-fork repositories, publicly authored PRs/issues, and contribution counts/active days in the latest 365 calendar dates, including the current UTC date.
- **Streak:** contribution days are counted from January of the account-creation year (2025 here), across year boundaries. Current streak allows an unfinished zero-contribution day today; a zero yesterday ends the current streak. Longest streak is within the stated history, not a claim about unobserved earlier dates.
- **Calendar:** daily counts visible without signing in on GitHub's public contribution calendar. If you expose anonymized private contributions publicly, those visible counts may be included. Private repository names/content are never fetched by this script.
- **Languages:** aggregated source bytes from owned, public, non-fork, non-archived repositories. The profile repository is excluded so its SVG files do not distort your language chart. The card is not a skill/proficiency rating and does not hide small percentages to exaggerate a language.
- **Snapshot:** `data/metrics.json` stores the fetched public counts, daily dates, source URLs and update timestamp. Screenshots from earlier times can differ from the current snapshot and its explicit rolling 365-day window.

The refresh script uses GitHub's REST API for repositories, languages and public issue/PR counts. The public contribution calendar HTML provides day-level activity without requiring an account-scoped token. That HTML is not a versioned API and can change; parsing is validated, and any fetch/parse failure stops the job before replacing old cards. It does not fabricate zero counts or publish error images.

## Maintenance and troubleshooting

| Symptom | Check |
|---|---|
| Broken image after upload | Confirm `assets/` is beside README, preserve capitalization, and upload its nested `badges/` and `metrics/` folders. |
| Workflow not visible | Confirm `.github/workflows/refresh-profile.yml` exists on the default branch and Actions are enabled. |
| Refresh passes but commit is denied | Repository/organization policies or branch protection may block bot writes. Check Actions workflow permissions and use the repository's normal permitted update process. No bypass is included. |
| Refresh fails while fetching | Retry manually later. API limits or GitHub availability can cause temporary failures; the last saved cards stay visible. |
| Calendar parsing error | GitHub may have changed its public calendar HTML. Update `CalendarParser` in `scripts/update_metrics.py`; do not replace unknown counts with zeros. |
| Card appears stale | Check its refresh date, the latest workflow run and repository history. GitHub's image cache may delay visible changes. |
| Stats differ from another service | Compare the time window, repository exclusions, anonymous private contribution visibility and streak timezone definitions above. |

To regenerate static artwork after changing colors or text:

```powershell
python scripts/build_theme.py
```

To refresh metrics locally (Python 3.10+; no package installation needed):

```powershell
python scripts/update_metrics.py
python -m unittest discover -s tests -v
```

Local unauthenticated API calls have lower rate limits. GitHub Actions uses the automatic `GITHUB_TOKEN` only for API quota and committing the resulting public-data assets to this profile repository. Never put a token in README, a badge URL or a committed file.

Theme constants are in `scripts/theme.py`: background `#0d1117`, panel `#11161c`, border `#29323a`, primary text `#f0f3ec`, secondary text `#a5afbc`, accent `#b5f36b`. Mobile artwork uses `<picture>` variants; individual technology badges naturally wrap. Fonts are system fonts, not a remote font dependency.

## Reference documentation

- [GitHub profile README requirements](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)
- [GitHub markup sanitization](https://github.com/github/markup#github-markup)
- [Automatic workflow token](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- [Scheduled workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [Public profile view counter](https://github.com/antonkomarev/github-profile-views-counter)

Prepared on 2026-09-09. This package has not been pushed to your GitHub account; the included workflow has been checked locally but has not run in your repository.
