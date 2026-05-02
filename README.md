# ⚡ ApplyTrack
A full stack web application that helps students track their internship and job applications in one place.

## Features
- 🔐 User authentication (username/password + Google OAuth)
- 📋 Add, edit, and delete job applications
- 📊 Dashboard with live stats (Applied, Interviews, Offers, Rejected)
- 🎯 Curated internship opportunities for Sri Lankan SE students
- 🌙 Professional dark dashboard with animations
- 🌐 Public landing page
- 🔒 Secure environment variable configuration

## Tech Stack
- **Backend** — Python, Flask, Flask-Login, Flask-Dance
- **Database** — SQLite, SQLAlchemy
- **Frontend** — HTML, CSS (custom, no frameworks)
- **Auth** — Google OAuth 2.0

## Setup
1. Clone the repo
```bash
   git clone https://github.com/pramilacz/applytrack.git
   cd applytrack
```

2. Create virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Create a `.env` file
