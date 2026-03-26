# Lenny Biography Portal History

```text
Version 1.2:
Core:
- Reorganized the project into a cleaner Flask-style structure with backend, templates, static, and data folders.
- Updated the codebase to use file-location-based paths so the app keeps working after files are moved.
- Cleaned out obsolete root-level duplicates from the old layout.

App Structure:
- Flask now serves templates from templates/ and assets from static/.
- Movie catalog data is now read from data/Movies/movies.json through /api/catalog.
- SQLite now lives in backend/data/portal_db.db.

Fixes and Optimization:
- Fixed db_setup.py so the database schema now includes synopsis, cast_list, and genres before harvest() updates them.
- Added a small shared database connection helper in run_portal.py.
- Refreshed the README to match the new structure while preserving version tracking.

Files moved or created:
- backend/run_portal.py
- backend/db_setup.py
- backend/Movies/scanner.py
- backend/data/portal_db.db
- templates/index.html
- templates/movies.html
- static/css/style.css
- static/js/movies_app.js
- static/thumbnails/
- data/Movies/movies.json

Files removed from active structure:
- run_portal.py
- db_setup.py
- index.html
- style.css
- Movies/index.html
- Movies/app.js
- Movies/scanner.py
- old root movies.json copies

Version 1.10.02:
Documentation:
- Added project documentation and version tracking notes.

Version 1.10.01:
Minor changes

Version 1.10:
Playback:
- Added browser-based video playback for supported movie files.

New files:
- app.js (moved functions out of Movies/index.html for better organization and functionality)

Version 1:
Core:
- Established the Flask-Python bridge to connect the D: drive to the web.
- Implemented scanner.py to auto-generate movies.json, eliminating manual entry.

UI:
- Created the Master Portal landing page and a basic movie grid.
- Built a simple two-page website with a master portal and a movie catalog.

Files:
- .gitignore
- Movies/index.html
- Movies/scanner.py
- index.html
- movies.json
- run_portal.py
- style.css
```
