SMARTSKILL MENTOR - BCA MINOR PROJECT
Features: profile (no login), career roadmap, learning pages, quizzes, score leaderboard, completion certificate, daily planner, dark mode, notifications, admin panel and CSV quiz export.

WINDOWS SETUP:
1. Extract ZIP and open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Run:
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
4. Open http://127.0.0.1:5000
5. First visit: complete Student Setup.

ADMIN:
Open /admin. Default demo PIN is 2468. Change ADMIN_PIN in app.py before sharing.
No student login/registration is included as requested.

DATABASE:
The app automatically creates smartskill_advanced.db. It is separate from your older smartskill.db, so the old project database is not overwritten. Back up this new database regularly.

NOTES:
This is a single-student local academic demo. Leaderboard summarizes quiz attempts/skills in this database; it is not a multi-student online ranking. Certificate is a project completion certificate, not an accredited qualification. For public hosting, configure a strong SECRET_KEY, change the admin PIN, and use persistent database storage.
