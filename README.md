# Mystique Portal History
```text
Version 1:
Core: Established the Flask-Python bridge to connect the D: drive to the web.
Automation: Implemented scanner.py to auto-generate movies.json, eliminating manual entry.
UI: Created the Master Portal landing page and a basic movie grid.
A simple two webpage website with 2 websites ie a master portal and a movie catalog
files: 
.gitignore (ignore some components of of the websites ie {__pycache__/ (Python's temp files)}, .env
Movies/index.html (the movie catalog funtioning with the help of flask bridge) 
Movies/scanner.py (a scanner to scan and pull movie names from specific folder)
index.html (master portal landing page, 2 links only)
movies.json (movie file list that is stored after running scanner.py)
run_portal.py (this runs scanner.py, updates the list then opens the localhost server)
style.css (basic styling)

Version 1.10:
This version now includes video playback for mp4 playback
New files:
app.js (moved functions from Movies/index.html to app.js for optimisation and functionality purposes)

version 1.10.01: minor changes
version 1.10.02: Documentation
```
