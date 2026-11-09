# AB Dashboard

Armor Bearers dashboard: what's next, what's due, the full calendar, training opportunities, and the playbook (Sunday basics, reference guide, SOPs).

Live page: https://jelksmba.github.io/ab-calendar/
Calendar feed: https://jelksmba.github.io/ab-calendar/ab-calendar.ics

## How it's built

- `src/dashboard.html` is the page source (same file published to claude.ai).
- `tools/build_page.sh src/dashboard.html` wraps it into `index.html` for GitHub Pages and adds the home-screen icon links.
- `tools/build_ics.py` builds `ab-calendar.ics`. Keep its dates in step with the page.
- `tools/make_icons.py` makes the home-screen icons.
- The latest sermon card sits between `<!-- SERMON:START -->` and `<!-- SERMON:END -->` in `src/dashboard.html`.
